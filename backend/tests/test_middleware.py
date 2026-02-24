"""Tests for middleware and error handling."""

from unittest.mock import MagicMock

import pytest

from app.api.middleware import error_handler
from app.clients.spacex_client import SpaceXAPIError


@pytest.mark.asyncio
async def test_trace_id_header_in_response(client):
    """Every response should contain an X-Trace-ID header."""
    response = await client.get("/health")
    assert "x-trace-id" in response.headers


@pytest.mark.asyncio
async def test_custom_trace_id_echoed(client):
    """When the request includes X-Trace-ID, it should be echoed back."""
    response = await client.get("/health", headers={"X-Trace-ID": "test-123"})
    assert response.headers.get("x-trace-id") == "test-123"


@pytest.mark.asyncio
async def test_error_handler_internal_error():
    """error_handler returns 500 for generic exceptions."""
    request = MagicMock()
    request.state = MagicMock()
    request.state.trace_id = "trace-abc"

    response = await error_handler(request, RuntimeError("Boom"))

    assert response.status_code == 500
    body = response.body.decode()
    assert "INTERNAL_ERROR" in body
    assert "trace-abc" in body


@pytest.mark.asyncio
async def test_error_handler_spacex_api_error():
    """error_handler returns 502 for SpaceX API server errors."""
    request = MagicMock()
    request.state = MagicMock()
    request.state.trace_id = "trace-xyz"

    response = await error_handler(request, SpaceXAPIError(500, "SpaceX down"))

    assert response.status_code == 502
    body = response.body.decode()
    assert "SPACEX_API_ERROR" in body


@pytest.mark.asyncio
async def test_error_handler_spacex_client_error():
    """error_handler preserves status code for SpaceX 4xx errors."""
    request = MagicMock()
    request.state = MagicMock()
    request.state.trace_id = "trace-404"

    response = await error_handler(request, SpaceXAPIError(404, "Not found"))

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_422_on_invalid_query_params(client):
    """Invalid query params should return 422 (FastAPI validation)."""
    response = await client.get("/api/launches?page=-5")
    assert response.status_code == 422
