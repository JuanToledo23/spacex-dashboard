from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")


@pytest.mark.asyncio
async def test_rockets_endpoint(client, sample_rockets, sample_launches):
    with patch("app.services.rocket_service.spacex_client") as mock_client:
        mock_client.get_rockets = AsyncMock(return_value=sample_rockets)
        mock_client.get_launches = AsyncMock(return_value=sample_launches)

        response = await client.get("/api/rockets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Falcon 1"


@pytest.mark.asyncio
async def test_launches_endpoint_returns_paginated(client, sample_launches):
    with patch("app.services.launch_service.cache") as cache_mock:
        cache_mock.get = AsyncMock(return_value=sample_launches)
        cache_mock.acquire_lock = AsyncMock(return_value=True)
        cache_mock.release_lock = AsyncMock()

        response = await client.get("/api/launches?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data


@pytest.mark.asyncio
async def test_error_format_on_invalid_page(client):
    response = await client.get("/api/launches?page=0")
    assert response.status_code == 422
