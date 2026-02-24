"""Tests for the cache layer (RedisCache and cached_fetch helper)."""

from unittest.mock import AsyncMock, patch

import pytest

from app.cache.helpers import cached_fetch
from app.cache.redis_cache import RedisCache

# ---------------------------------------------------------------------------
# RedisCache unit tests
# ---------------------------------------------------------------------------


class TestRedisCache:
    @pytest.mark.asyncio
    async def test_get_returns_none_when_key_missing(self):
        cache = RedisCache()
        cache._redis = AsyncMock()
        cache._redis.get = AsyncMock(return_value=None)

        result = await cache.get("missing:key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_deserialises_json(self):
        cache = RedisCache()
        cache._redis = AsyncMock()
        cache._redis.get = AsyncMock(return_value='{"hello": "world"}')

        result = await cache.get("my:key")
        assert result == {"hello": "world"}

    @pytest.mark.asyncio
    async def test_set_serialises_to_json(self):
        cache = RedisCache()
        cache._redis = AsyncMock()
        cache._redis.set = AsyncMock()

        await cache.set("my:key", {"a": 1}, ttl=60)
        cache._redis.set.assert_awaited_once()
        args = cache._redis.set.call_args
        assert args[0][0] == "my:key"
        assert '"a": 1' in args[0][1]
        assert args[1]["ex"] == 60

    @pytest.mark.asyncio
    async def test_acquire_lock_returns_bool(self):
        cache = RedisCache()
        cache._redis = AsyncMock()
        cache._redis.set = AsyncMock(return_value=True)

        result = await cache.acquire_lock("my:key")
        assert result is True

    @pytest.mark.asyncio
    async def test_release_lock_deletes_key(self):
        cache = RedisCache()
        cache._redis = AsyncMock()
        cache._redis.delete = AsyncMock()

        await cache.release_lock("my:key")
        cache._redis.delete.assert_awaited_once_with("lock:my:key")

    @pytest.mark.asyncio
    async def test_health_check_returns_true(self):
        cache = RedisCache()
        cache._redis = AsyncMock()
        cache._redis.ping = AsyncMock(return_value=True)

        assert await cache.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_returns_false_on_error(self):
        cache = RedisCache()
        cache._redis = AsyncMock()
        cache._redis.ping = AsyncMock(side_effect=ConnectionError("down"))

        assert await cache.health_check() is False


# ---------------------------------------------------------------------------
# cached_fetch helper tests
# ---------------------------------------------------------------------------


class TestCachedFetch:
    def _make_cache(self, **overrides):
        m = AsyncMock()
        m.get = AsyncMock(return_value=None)
        m.set = AsyncMock()
        m.acquire_lock = AsyncMock(return_value=True)
        m.release_lock = AsyncMock()
        for k, v in overrides.items():
            setattr(m, k, v)
        return m

    @pytest.mark.asyncio
    async def test_returns_cached_data_on_hit(self):
        cm = self._make_cache(get=AsyncMock(return_value={"cached": True}))
        with patch("app.cache.helpers.cache", cm):
            result = await cached_fetch("key", 60, AsyncMock())
        assert result == {"cached": True}

    @pytest.mark.asyncio
    async def test_calls_fetch_fn_on_miss(self):
        cm = self._make_cache()
        fetch_fn = AsyncMock(return_value=[1, 2, 3])
        with patch("app.cache.helpers.cache", cm):
            result = await cached_fetch("key", 120, fetch_fn)
        assert result == [1, 2, 3]
        fetch_fn.assert_awaited_once()
        cm.set.assert_awaited_once_with("key", [1, 2, 3], 120)

    @pytest.mark.asyncio
    async def test_waits_and_retries_when_lock_unavailable(self):
        cm = self._make_cache(
            get=AsyncMock(side_effect=[None, {"from_other": True}]),
            acquire_lock=AsyncMock(return_value=False),
        )
        with (
            patch("app.cache.helpers.cache", cm),
            patch("app.cache.helpers.asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await cached_fetch("key", 60, AsyncMock())
        assert result == {"from_other": True}

    @pytest.mark.asyncio
    async def test_releases_lock_even_on_error(self):
        cm = self._make_cache()
        fetch_fn = AsyncMock(side_effect=RuntimeError("boom"))
        with patch("app.cache.helpers.cache", cm):
            with pytest.raises(RuntimeError, match="boom"):
                await cached_fetch("key", 60, fetch_fn)
        cm.release_lock.assert_awaited_once()
