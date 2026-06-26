from __future__ import annotations

import pytest

from restful_booker.clients.auth_client import AuthClient
from restful_booker.config.settings import settings
from restful_booker.models.auth import AuthFailure, AuthSuccess, TokenRequest


@pytest.mark.auth
@pytest.mark.smoke
def test_should_create_token_with_valid_credentials(auth_client: AuthClient) -> None:
    """POST /auth with valid credentials should return a token."""
    credentials = TokenRequest(username=settings.username, password=settings.password)
    response = auth_client.create_token(credentials)
    assert response.status == 200

    auth = AuthSuccess.model_validate(response.json())
    assert auth.token


@pytest.mark.auth
def test_should_fail_with_invalid_credentials(auth_client: AuthClient) -> None:
    """POST /auth with invalid credentials should return a reason."""
    credentials = TokenRequest(username="wrong", password="wrong")
    response = auth_client.create_token(credentials)
    assert response.status == 200

    auth_failure = AuthFailure.model_validate(response.json())
    assert auth_failure.reason
