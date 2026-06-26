"""Shared transport behavior for API resource clients."""

from __future__ import annotations

import json
import logging
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

logger = logging.getLogger(__name__)

_SENSITIVE_KEYS = {
    "authorization",
    "cookie",
    "password",
    "set-cookie",
    "token",
}


def _attach_to_allure(name: str, content: str) -> None:
    """Attach request/response content when Allure reporting is enabled."""
    try:
        import allure
    except ImportError:
        return

    allure.attach(
        content,
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def _redact_sensitive(value: Any) -> Any:
    """Return a copy of nested data with credentials and tokens redacted."""
    if isinstance(value, dict):
        return {
            key: "<redacted>" if str(key).lower() in _SENSITIVE_KEYS else _redact_sensitive(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_redact_sensitive(item) for item in value]
    return value


def _safe_attachment(value: Any) -> str:
    """Serialize data for an Allure attachment after redacting secrets."""
    return json.dumps(_redact_sensitive(value), indent=2, default=str)


def _safe_response_body(response: APIResponse) -> str:
    """Best-effort response serialization with sensitive values redacted."""
    try:
        return _safe_attachment(response.json())
    except Exception:
        try:
            return response.text()
        except Exception:
            return "<no body>"


class BaseClient:
    """Base wrapper around Playwright's ``APIRequestContext``."""

    def __init__(self, request_context: APIRequestContext) -> None:
        self._request = request_context

    def get_common_headers(self) -> dict[str, str]:
        """Headers applied to every request unless overridden per call."""
        return {"Accept": "application/json"}

    def _do(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        data: Any = None,
    ) -> APIResponse:
        """Perform a request and return the raw Playwright response."""
        merged = {**self.get_common_headers(), **(headers or {})}
        logger.info("→ %s %s", method.upper(), url)

        response = self._request.fetch(
            url,
            method=method.upper(),
            headers=merged,
            data=data,
        )

        logger.info("← %s", response.status)
        _attach_to_allure(
            f"Request {method.upper()} {url}",
            _safe_attachment(data if data is not None else {}),
        )
        _attach_to_allure(
            f"Response {response.status} {method.upper()} {url}",
            _safe_response_body(response),
        )
        return response
