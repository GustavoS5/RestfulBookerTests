"""Pydantic schemas for Restful-Booker authentication responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    """Auth request body."""

    username: str
    password: str


class AuthSuccess(BaseModel):
    """Successful auth response."""

    token: str = Field(min_length=1)


class AuthFailure(BaseModel):
    """Failed auth response."""

    reason: str
