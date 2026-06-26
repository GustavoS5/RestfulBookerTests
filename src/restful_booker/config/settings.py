"""Environment-driven settings for the test suite."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime configuration."""

    api_base_url: str
    username: str
    password: str


def _get(key: str, default: str) -> str:
    """Read an environment variable with a fallback."""
    value = os.getenv(key)
    return value if value else default


def load_settings() -> Settings:
    """Load settings from environment variables."""
    return Settings(
        api_base_url=_get("API_BASE_URL", "https://restful-booker.herokuapp.com"),
        username=_get("API_USERNAME", "admin"),
        password=_get("API_PASSWORD", "password123"),
    )


settings = load_settings()
