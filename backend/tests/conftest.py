from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


def _make_cache_mock():
    """Create a mock that mimics the RedisCache interface."""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock()
    mock.acquire_lock = AsyncMock(return_value=True)
    mock.release_lock = AsyncMock()
    mock.health_check = AsyncMock(return_value=True)
    mock.connect = AsyncMock()
    mock.disconnect = AsyncMock()
    mock._redis = None  # Default to None; tests can override
    return mock


@pytest.fixture
def mock_cache():
    """Patch the cache singleton everywhere it is imported."""
    mock = _make_cache_mock()
    with (
        patch("app.cache.redis_cache.cache", mock),
        patch("app.cache.helpers.cache", mock),
        patch("app.api.rate_limit.cache", mock),
    ):
        yield mock


@pytest.fixture
def sample_rockets():
    return [
        {
            "id": "5e9d0d95eda69955f709bf1c",
            "name": "Falcon 1",
            "type": "rocket",
            "active": False,
            "cost_per_launch": 6700000,
            "first_flight": "2006-03-24",
            "description": "The Falcon 1 was an expendable launch system.",
        },
        {
            "id": "5e9d0d95eda69973a809d1ec",
            "name": "Falcon 9",
            "type": "rocket",
            "active": True,
            "cost_per_launch": 50000000,
            "first_flight": "2010-06-04",
            "description": "Falcon 9 is a two-stage rocket.",
        },
    ]


@pytest.fixture
def sample_launches():
    return [
        {
            "id": "launch1",
            "name": "FalconSat",
            "date_utc": "2006-03-24T22:30:00.000Z",
            "success": False,
            "upcoming": False,
            "rocket": "5e9d0d95eda69955f709bf1c",
            "details": "Engine failure.",
        },
        {
            "id": "launch2",
            "name": "Starlink Mission",
            "date_utc": "2023-06-15T10:00:00.000Z",
            "success": True,
            "upcoming": False,
            "rocket": "5e9d0d95eda69973a809d1ec",
            "details": None,
        },
    ]


@pytest.fixture
async def client(mock_cache):
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
