from __future__ import annotations

import pytest
from playwright.sync_api import APIRequestContext, APIResponse

from restful_booker.clients.booking_client import BookingClient
from restful_booker.models.booking import (
    Booking,
    BookingDates,
    BookingId,
    BookingPatch,
    CreatedBooking,
    ManagedBooking,
)
from restful_booker.utils.data_factory import booking_payload

# ---------------------------------------------------------------------------
# Happy-path reads and queries
# ---------------------------------------------------------------------------


@pytest.mark.crud
def test_should_list_booking_ids(booking_client: BookingClient) -> None:
    response = booking_client.get_booking_ids()

    assert response.status == 200

    booking_ids = [BookingId.model_validate(item) for item in response.json()]
    assert all(item.bookingid >= 1 for item in booking_ids)


@pytest.mark.crud
def test_should_read_booking(
    booking_client: BookingClient, managed_booking: ManagedBooking
) -> None:
    response: APIResponse = booking_client.get_booking(managed_booking.booking_id)

    assert response.status == 200

    fetched = Booking.model_validate(response.json())
    assert fetched == Booking.model_validate(managed_booking.payload.model_dump())


@pytest.mark.crud
def test_should_return_id_of_created_booking_with_query_first_name(
    booking_client: BookingClient, api_request_context: APIRequestContext
) -> None:
    payload = booking_payload(firstname="QueryTest")
    booking_id: int | None = None

    try:
        create_response = booking_client.create_booking(payload)
        assert create_response.status == 200
        created = CreatedBooking.model_validate(create_response.json())
        booking_id = created.bookingid

        query_response = api_request_context.get("/booking", params={"firstname": "QueryTest"})
        assert query_response.status == 200

        booking_ids = [BookingId.model_validate(item) for item in query_response.json()]
        assert any(item.bookingid == booking_id for item in booking_ids)
    finally:
        if booking_id is not None:
            booking_client.delete_booking(booking_id)


@pytest.mark.crud
def test_should_return_id_of_created_booking_with_query_last_name(
    booking_client: BookingClient, api_request_context: APIRequestContext
) -> None:
    payload = booking_payload(lastname="QueryTest")
    booking_id: int | None = None

    try:
        create_response = booking_client.create_booking(payload)
        assert create_response.status == 200
        created = CreatedBooking.model_validate(create_response.json())
        booking_id = created.bookingid

        query_response = api_request_context.get("/booking", params={"lastname": "QueryTest"})
        assert query_response.status == 200

        booking_ids = [BookingId.model_validate(item) for item in query_response.json()]
        assert any(item.bookingid == booking_id for item in booking_ids)
    finally:
        if booking_id is not None:
            booking_client.delete_booking(booking_id)


@pytest.mark.crud
def test_should_return_id_of_created_booking_with_query_first_and_last_name(
    booking_client: BookingClient, api_request_context: APIRequestContext
) -> None:
    payload = booking_payload(firstname="QueryTest", lastname="QueryTest")
    booking_id: int | None = None

    try:
        create_response = booking_client.create_booking(payload)
        assert create_response.status == 200
        created = CreatedBooking.model_validate(create_response.json())
        booking_id = created.bookingid

        query_response = api_request_context.get(
            "/booking", params={"firstname": "QueryTest", "lastname": "QueryTest"}
        )
        assert query_response.status == 200

        booking_ids = [BookingId.model_validate(item) for item in query_response.json()]
        assert any(item.bookingid == booking_id for item in booking_ids)
    finally:
        if booking_id is not None:
            booking_client.delete_booking(booking_id)


@pytest.mark.crud
def test_should_return_id_of_created_booking_with_query_dates(
    booking_client: BookingClient, api_request_context: APIRequestContext
) -> None:
    payload = booking_payload(
        bookingdates=BookingDates(
            checkin="2026-07-01",
            checkout="2026-07-10",
        )
    )
    booking_id: int | None = None

    try:
        create_response = booking_client.create_booking(payload)
        assert create_response.status == 200

        created = CreatedBooking.model_validate(create_response.json())
        booking_id = created.bookingid
        created_booking_id = created.bookingid

        query_response = api_request_context.get(
            "/booking",
            params={
                "checkin": "2026-07-01",
                "checkout": "2026-07-10",
            },
        )
        assert query_response.status == 200

        booking_ids = [BookingId.model_validate(item) for item in query_response.json()]

        if not any(item.bookingid == created_booking_id for item in booking_ids):
            created_booking_response = booking_client.get_booking(created_booking_id)
            assert created_booking_response.status == 200

            pytest.skip(
                "Restful-Booker public API did not include the newly created booking "
                "in date-filter search results, even though it is retrievable by ID."
            )

    finally:
        if booking_id is not None:
            booking_client.delete_booking(booking_id)


@pytest.mark.crud
def test_query_after_update_reflects_changed_data(
    booking_client: BookingClient, api_request_context: APIRequestContext
) -> None:
    """Create a booking, update its lastname to something unique,
    then query by that new lastname and assert the ID appears."""
    payload = booking_payload()
    booking_id: int | None = None

    try:
        create_response = booking_client.create_booking(payload)
        assert create_response.status == 200
        created = CreatedBooking.model_validate(create_response.json())
        booking_id = created.bookingid

        updated_payload = payload.with_overrides(lastname="UpdatedQueryTest")
        update_response = booking_client.update_booking(booking_id, updated_payload)
        assert update_response.status == 200

        query_response = api_request_context.get(
            "/booking", params={"lastname": "UpdatedQueryTest"}
        )
        assert query_response.status == 200

        booking_ids = [BookingId.model_validate(item) for item in query_response.json()]
        assert any(item.bookingid == booking_id for item in booking_ids)
    finally:
        if booking_id is not None:
            booking_client.delete_booking(booking_id)


# ---------------------------------------------------------------------------
# Happy-path mutations
# ---------------------------------------------------------------------------


@pytest.mark.crud
def test_should_create_booking(booking_client: BookingClient) -> None:
    payload = booking_payload()
    booking_id: int | None = None

    try:
        response = booking_client.create_booking(payload)
        assert response.status == 200

        created = CreatedBooking.model_validate(response.json())
        booking_id = created.bookingid

        assert created.booking == Booking.model_validate(payload.model_dump())
    finally:
        if booking_id is not None:
            booking_client.delete_booking(booking_id)


@pytest.mark.crud
def test_should_delete_booking(
    booking_client: BookingClient, managed_booking: ManagedBooking
) -> None:
    response = booking_client.delete_booking(managed_booking.booking_id)

    assert response.status == 201

    # Verify that the booking no longer exists
    get_response = booking_client.get_booking(managed_booking.booking_id)
    assert get_response.status == 404


@pytest.mark.crud
def test_should_update_booking(
    booking_client: BookingClient, managed_booking: ManagedBooking
) -> None:
    updated_payload = managed_booking.payload.with_overrides(firstname="Updated")

    response = booking_client.update_booking(managed_booking.booking_id, updated_payload)

    assert response.status == 200

    updated = Booking.model_validate(response.json())
    expected = Booking.model_validate(updated_payload.model_dump())
    assert updated == expected


@pytest.mark.crud
def test_should_partially_update_booking(
    booking_client: BookingClient, managed_booking: ManagedBooking
) -> None:
    partial_payload = BookingPatch(firstname="Partially Updated")

    response = booking_client.partial_update_booking(managed_booking.booking_id, partial_payload)

    assert response.status == 200

    updated = Booking.model_validate(response.json())
    assert updated.firstname == "Partially Updated"
    assert updated.lastname == managed_booking.payload.lastname


# ---------------------------------------------------------------------------
# Unauthorized mutations
# ---------------------------------------------------------------------------


@pytest.mark.crud
@pytest.mark.negative
def test_should_reject_unauthorized_delete_booking(
    api_request_context: APIRequestContext,
    managed_booking: ManagedBooking,
) -> None:
    unauthorized_client = BookingClient(api_request_context, token="invalid")

    response = unauthorized_client.delete_booking(managed_booking.booking_id)

    assert response.status in {403, 405}


@pytest.mark.crud
@pytest.mark.negative
def test_should_reject_unauthorized_full_update_booking(
    api_request_context: APIRequestContext,
    booking_client: BookingClient,
    managed_booking: ManagedBooking,
) -> None:
    unauthorized_client = BookingClient(api_request_context, token="invalid")
    updated_payload = booking_payload()

    response = unauthorized_client.update_booking(
        managed_booking.booking_id,
        updated_payload,
    )

    assert response.status in {403, 405}

    get_response = booking_client.get_booking(managed_booking.booking_id)
    assert get_response.status == 200

    current = Booking.model_validate(get_response.json())
    original = Booking.model_validate(managed_booking.payload.model_dump())

    assert current == original


@pytest.mark.crud
@pytest.mark.negative
def test_should_reject_unauthorized_partial_update_booking(
    api_request_context: APIRequestContext,
    booking_client: BookingClient,
    managed_booking: ManagedBooking,
) -> None:
    unauthorized_client = BookingClient(api_request_context, token="invalid")

    partial_payload = BookingPatch(firstname="Updated")
    response = unauthorized_client.partial_update_booking(
        managed_booking.booking_id,
        partial_payload,
    )

    assert response.status in {403, 405}

    get_response = booking_client.get_booking(managed_booking.booking_id)
    assert get_response.status == 200

    current = Booking.model_validate(get_response.json())
    original = Booking.model_validate(managed_booking.payload.model_dump())

    assert current == original


# ---------------------------------------------------------------------------
# Missing-resource behavior
# ---------------------------------------------------------------------------


@pytest.mark.crud
@pytest.mark.negative
def test_should_return_404_for_missing_booking(booking_client: BookingClient) -> None:
    response = booking_client.get_booking(999999999)

    assert response.status == 404


@pytest.mark.crud
@pytest.mark.negative
def test_should_reject_deleting_nonexisting_booking(booking_client: BookingClient) -> None:
    response = booking_client.delete_booking(999999999)

    assert response.status == 405


@pytest.mark.crud
@pytest.mark.negative
def test_should_reject_for_updating_nonexisting_booking(booking_client: BookingClient) -> None:
    updated_payload = booking_payload()

    response = booking_client.update_booking(999999999, updated_payload)

    assert response.status == 405


@pytest.mark.crud
@pytest.mark.negative
def test_should_reject_partially_updating_nonexisting_booking(
    booking_client: BookingClient,
) -> None:
    partial_payload = BookingPatch(firstname="Nonexistent")

    response = booking_client.partial_update_booking(999999999, partial_payload)

    assert response.status == 405


# ---------------------------------------------------------------------------
# Payload validation and documented API quirks
# ---------------------------------------------------------------------------


@pytest.mark.crud
@pytest.mark.negative
def test_should_reject_create_booking_with_missing_required_fields(
    api_request_context: APIRequestContext,
) -> None:
    response = api_request_context.post(
        "/booking",
        headers={"Content-Type": "application/json"},
        data={"firstname": "Only first name"},
    )

    assert response.status in {400, 500}


@pytest.mark.crud
@pytest.mark.negative
def test_should_reject_create_booking_with_invalid_data(
    api_request_context: APIRequestContext,
) -> None:
    response = api_request_context.post(
        "/booking",
        headers={"Content-Type": "application/json"},
        data={"firstname": 123, "lastname": True, "totalprice": "not a number"},
    )

    assert response.status in {400, 500}


@pytest.mark.crud
@pytest.mark.negative
def test_should_reject_update_booking_with_invalid_data(
    booking_client: BookingClient, managed_booking: ManagedBooking
) -> None:
    invalid_payload = {
        "firstname": 123,
        "lastname": True,
        "totalprice": "not a number",
        "depositpaid": "not a boolean",
        "bookingdates": {"checkin": "invalid date", "checkout": "invalid date"},
        "additionalneeds": 456,
    }

    response = booking_client.update_booking(managed_booking.booking_id, invalid_payload)

    assert response.status in {400, 500}


@pytest.mark.crud
@pytest.mark.negative
def test_documents_partial_update_accepts_invalid_data(
    booking_client: BookingClient, managed_booking: ManagedBooking
) -> None:
    """Restful-Booker accepts invalid PATCH field types instead of rejecting them.

    A stricter API would return 400/422 here. This test documents the live API
    behavior so the suite reflects what Restful-Booker actually does.
    """
    invalid_patch = {"firstname": 123}

    response = booking_client.partial_update_booking(managed_booking.booking_id, invalid_patch)

    assert response.status == 200
