"""Shared pytest fixtures for API context, clients, auth, and test data."""

from __future__ import annotations

import logging
from collections.abc import Generator

import pytest
from playwright.sync_api import APIRequestContext, Playwright

from restful_booker.clients.auth_client import AuthClient
from restful_booker.clients.booking_client import BookingClient
from restful_booker.config.settings import settings
from restful_booker.models.auth import AuthSuccess, TokenRequest
from restful_booker.models.booking import CreatedBooking, ManagedBooking
from restful_booker.utils.data_factory import booking_payload

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> Generator[APIRequestContext]:
    """Playwright request context configured with the API base URL."""
    context = playwright.request.new_context(base_url=settings.api_base_url)
    logger.info("Created API context for %s", settings.api_base_url)
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def auth_token(api_request_context: APIRequestContext) -> str:
    """Session token used by authenticated booking tests."""
    client = AuthClient(api_request_context)
    response = client.create_token(
        TokenRequest(username=settings.username, password=settings.password)
    )
    assert response.ok, f"Auth failed during session setup: HTTP {response.status}"
    token = AuthSuccess.model_validate(response.json()).token
    logger.info("Acquired session token for %s", settings.username)
    return token


@pytest.fixture(scope="session")
def auth_client(api_request_context: APIRequestContext) -> AuthClient:
    """Unauthenticated client for auth endpoint tests."""
    return AuthClient(api_request_context)


@pytest.fixture(scope="session")
def booking_client(api_request_context: APIRequestContext, auth_token: str) -> BookingClient:
    """Authenticated booking client for CRUD tests."""
    return BookingClient(api_request_context, token=auth_token)


@pytest.fixture
def managed_booking(booking_client: BookingClient) -> Generator[ManagedBooking]:
    """Create a booking for one test and clean it up afterward."""
    payload = booking_payload()
    response = booking_client.create_booking(payload)
    assert response.ok, f"Setup booking creation failed: HTTP {response.status}"
    created = CreatedBooking.model_validate(response.json())

    managed = ManagedBooking(booking_id=created.bookingid, payload=payload)
    yield managed

    # Best-effort cleanup: delete tests may already have removed the booking.
    try:
        cleanup_response = booking_client.delete_booking(managed.booking_id)
        if not cleanup_response.ok:
            logger.info(
                "Cleanup returned HTTP %s for booking %s",
                cleanup_response.status,
                managed.booking_id,
            )
    except Exception:
        logger.exception("Cleanup failed for booking %s", managed.booking_id)
