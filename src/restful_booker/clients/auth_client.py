"""Client for the Restful-Booker authentication endpoint."""

from __future__ import annotations

from playwright.sync_api import APIResponse

from restful_booker.clients.base_client import BaseClient
from restful_booker.models.auth import TokenRequest


class AuthClient(BaseClient):
    """Thin wrapper around ``POST /auth``."""

    AUTH_PATH = "/auth"

    def create_token(self, credentials: TokenRequest) -> APIResponse:
        """Create an auth token from username/password credentials."""
        return self._do(
            "post",
            self.AUTH_PATH,
            headers={"Content-Type": "application/json"},
            data=credentials.model_dump(),
        )
