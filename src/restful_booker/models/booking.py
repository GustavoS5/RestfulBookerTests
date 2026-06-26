"""Pydantic schemas for the Restful-Booker booking resource."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base schema that rejects undocumented fields."""

    model_config = ConfigDict(extra="forbid")


class BookingDates(StrictModel):
    """Check-in and check-out dates."""

    checkin: str
    checkout: str


class BookingPayload(StrictModel):
    """Complete payload for create and full update requests."""

    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str = ""

    def with_overrides(self, **kwargs: Any) -> BookingPayload:
        """Return a revalidated copy with selected fields changed."""
        return BookingPayload.model_validate({**self.model_dump(), **kwargs})


class BookingPatch(StrictModel):
    """Partial payload for PATCH requests."""

    firstname: str | None = None
    lastname: str | None = None
    totalprice: int | None = None
    depositpaid: bool | None = None
    bookingdates: BookingDates | None = None
    additionalneeds: str | None = None


class Booking(StrictModel):
    """Booking resource returned by the API."""

    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str = ""


class CreatedBooking(StrictModel):
    """Create response wrapper."""

    bookingid: int = Field(ge=1)
    booking: Booking


class BookingId(StrictModel):
    """Booking ID item returned by the list endpoint."""

    bookingid: int = Field(ge=1)


@dataclass(frozen=True)
class ManagedBooking:
    """Booking created by a fixture, plus the payload used to create it."""

    booking_id: int
    payload: BookingPayload
