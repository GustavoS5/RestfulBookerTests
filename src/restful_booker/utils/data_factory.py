"""Factories for valid, distinctive booking test data."""

from __future__ import annotations

import secrets
from datetime import timedelta
from typing import Any

from faker import Faker

from restful_booker.models.booking import (
    BookingDates,
    BookingPatch,
    BookingPayload,
)

_faker = Faker()

_ADDITIONAL_NEEDS = ["Breakfast", "Lunch", "Dinner", "Parking", "Late checkout", "Extra blankets"]


def booking_dates() -> BookingDates:
    """Return valid check-in and check-out dates."""
    checkin = _faker.date_between(start_date="today", end_date="+30d")
    checkout = checkin + timedelta(days=_faker.random_int(min=1, max=10))
    return BookingDates(checkin=checkin.isoformat(), checkout=checkout.isoformat())


def booking_payload(**overrides: Any) -> BookingPayload:
    """Return a complete booking payload, with optional field overrides."""
    payload = BookingPayload(
        firstname=_faker.first_name(),
        lastname=_faker.last_name(),
        totalprice=_faker.random_int(min=50, max=2000),
        depositpaid=_faker.boolean(),
        bookingdates=booking_dates(),
        additionalneeds=_faker.random.choice(_ADDITIONAL_NEEDS),
    )
    return payload.with_overrides(**overrides)


def booking_patch(**overrides: Any) -> BookingPatch:
    """Return a partial-update payload."""
    return BookingPatch(
        **{
            "firstname": _faker.first_name(),
            "additionalneeds": f"{secrets.token_hex(4)}-PROVIDED",
            **overrides,
        }
    )
