"""Tests for the rate-limiting helper."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.rate_limit import check_rate_limit


def _make_request(ip: str = "127.0.0.1") -> MagicMock:
    request = MagicMock()
    request.client = MagicMock()
    request.client.host = ip
    return request


class TestCheckRateLimit:
    @pytest.mark.asyncio
    async def test_allows_within_limit(self):
        redis_mock = AsyncMock()
        redis_mock.incr = AsyncMock(return_value=1)
        redis_mock.expire = AsyncMock()
        cache_mock = MagicMock()
        cache_mock._redis = redis_mock

        with patch("app.api.rate_limit.cache", cache_mock):
            request = _make_request()
            await check_rate_limit(request, max_requests=10, window_seconds=60)

    @pytest.mark.asyncio
    async def test_raises_429_when_exceeded(self):
        redis_mock = AsyncMock()
        redis_mock.incr = AsyncMock(return_value=11)
        redis_mock.expire = AsyncMock()
        cache_mock = MagicMock()
        cache_mock._redis = redis_mock

        with patch("app.api.rate_limit.cache", cache_mock):
            request = _make_request()
            with pytest.raises(HTTPException) as exc_info:
                await check_rate_limit(request, max_requests=10, window_seconds=60)
            assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_sets_expiry_on_first_request(self):
        redis_mock = AsyncMock()
        redis_mock.incr = AsyncMock(return_value=1)
        redis_mock.expire = AsyncMock()
        cache_mock = MagicMock()
        cache_mock._redis = redis_mock

        with patch("app.api.rate_limit.cache", cache_mock):
            request = _make_request()
            await check_rate_limit(request, prefix="rl:test", max_requests=10, window_seconds=30)
            redis_mock.expire.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_fails_open_when_redis_unavailable(self):
        cache_mock = MagicMock()
        cache_mock._redis = None

        with patch("app.api.rate_limit.cache", cache_mock):
            request = _make_request()
            await check_rate_limit(request, max_requests=1, window_seconds=60)

    @pytest.mark.asyncio
    async def test_fails_open_on_redis_error(self):
        redis_mock = AsyncMock()
        redis_mock.incr = AsyncMock(side_effect=ConnectionError("down"))
        cache_mock = MagicMock()
        cache_mock._redis = redis_mock

        with patch("app.api.rate_limit.cache", cache_mock):
            request = _make_request()
            await check_rate_limit(request, max_requests=1, window_seconds=60)
