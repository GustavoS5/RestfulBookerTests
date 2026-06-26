from __future__ import annotations

import pytest
from playwright.sync_api import APIRequestContext


@pytest.mark.smoke
def test_should_ping_api(api_request_context: APIRequestContext) -> None:
    response = api_request_context.get("/ping")

    assert response.status == 201
    assert response.ok
