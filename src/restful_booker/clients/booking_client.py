"""Client for the Restful-Booker ``/booking`` resource."""

from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from restful_booker.clients.base_client import BaseClient
from restful_booker.models.booking import BookingPatch, BookingPayload


class BookingClient(BaseClient):
    """Client for the Restful-Booker booking resource."""

    BOOKING_PATH = "/booking"

    def __init__(self, request_context: APIRequestContext, token: str | None = None) -> None:
        super().__init__(request_context)
        self._token = token

    def _auth_headers(self) -> dict[str, str]:
        """Return the cookie auth header when a token is available."""
        return {"Cookie": f"token={self._token}"} if self._token else {}

    def get_booking_ids(self) -> APIResponse:
        """List booking IDs."""
        return self._do("get", self.BOOKING_PATH)

    def get_booking(self, booking_id: int) -> APIResponse:
        """Get one booking by ID."""
        return self._do("get", f"{self.BOOKING_PATH}/{booking_id}")

    def create_booking(self, payload: BookingPayload) -> APIResponse:
        """Create a booking."""
        return self._do(
            "post",
            self.BOOKING_PATH,
            headers={"Content-Type": "application/json"},
            data=payload.model_dump(),
        )

    def update_booking(
        self, booking_id: int, payload: BookingPayload | dict[str, Any]
    ) -> APIResponse:
        """Replace a booking with a complete payload."""
        data = payload.model_dump() if isinstance(payload, BookingPayload) else payload
        return self._do(
            "put",
            f"{self.BOOKING_PATH}/{booking_id}",
            headers={"Content-Type": "application/json", **self._auth_headers()},
            data=data,
        )

    def partial_update_booking(
        self, booking_id: int, patch: BookingPatch | dict[str, Any]
    ) -> APIResponse:
        """Update selected booking fields."""
        data = patch.model_dump(exclude_none=True) if isinstance(patch, BookingPatch) else patch
        return self._do(
            "patch",
            f"{self.BOOKING_PATH}/{booking_id}",
            headers={"Content-Type": "application/json", **self._auth_headers()},
            data=data,
        )

    def delete_booking(self, booking_id: int) -> APIResponse:
        """Delete a booking by ID."""
        return self._do("delete", f"{self.BOOKING_PATH}/{booking_id}", headers=self._auth_headers())
