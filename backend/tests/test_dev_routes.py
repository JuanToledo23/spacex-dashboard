"""Tests for the dev/trigger-error easter egg endpoint."""

import pytest


@pytest.mark.asyncio
async def test_trigger_error_404(client):
    """Returns 404 with structured error body."""
    resp = await client.get("/api/dev/trigger-error?code=404")
    assert resp.status_code == 404
    data = resp.json()
    assert data["code"] == "RESOURCE_NOT_FOUND"
    assert "404" in data["message"]
    assert "trace_id" in data


@pytest.mark.asyncio
async def test_trigger_error_500(client):
    """Returns 500 with structured error body."""
    resp = await client.get("/api/dev/trigger-error?code=500")
    assert resp.status_code == 500
    data = resp.json()
    assert data["code"] == "INTERNAL_ERROR"
    assert "500" in data["message"]
    assert "trace_id" in data


@pytest.mark.asyncio
async def test_trigger_error_502(client):
    """Returns 502 with structured error body."""
    resp = await client.get("/api/dev/trigger-error?code=502")
    assert resp.status_code == 502
    data = resp.json()
    assert data["code"] == "BAD_GATEWAY"


@pytest.mark.asyncio
async def test_trigger_error_503(client):
    """Returns 503 with structured error body."""
    resp = await client.get("/api/dev/trigger-error?code=503")
    assert resp.status_code == 503
    data = resp.json()
    assert data["code"] == "SERVICE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_trigger_error_unknown_defaults_to_500(client):
    """Unknown code defaults to 500."""
    resp = await client.get("/api/dev/trigger-error?code=invalid")
    assert resp.status_code == 500
    data = resp.json()
    assert data["code"] == "INTERNAL_ERROR"
