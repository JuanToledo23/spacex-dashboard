"""Redis cache layer: JSON get/set with TTL, distributed locks for stampede prevention.

Singleton `cache` is used by helpers, middleware, and rate_limit. All methods
fail gracefully (return None / no-op) when Redis is unavailable.
"""

import json

import redis.asyncio as redis

from app.config import settings


class RedisCache:
    """Async Redis wrapper. Connect/disconnect via lifespan; get/set for cache-aside."""

    def __init__(self):
        self._redis: redis.Redis | None = None

    async def connect(self):
        self._redis = redis.from_url(settings.redis_url, decode_responses=True)

    async def disconnect(self):
        if self._redis:
            await self._redis.close()

    async def get(self, key: str) -> dict | list | None:
        """Return deserialized JSON or None. Returns None if Redis unavailable."""
        if not self._redis:
            return None
        raw = await self._redis.get(key)
        return json.loads(raw) if raw else None

    async def set(self, key: str, value: dict | list, ttl: int = 300):
        """Store JSON-serializable value with TTL (seconds). No-op if Redis unavailable."""
        if not self._redis:
            return
        await self._redis.set(key, json.dumps(value, default=str), ex=ttl)

    async def acquire_lock(self, key: str, ttl: int = 30) -> bool:
        """Acquire distributed lock (SET NX). Returns True if acquired, False if held by another."""
        if not self._redis:
            return False
        return await self._redis.set(f"lock:{key}", "1", ex=ttl, nx=True)

    async def release_lock(self, key: str):
        """Release lock. No-op if Redis unavailable."""
        if not self._redis:
            return
        await self._redis.delete(f"lock:{key}")

    async def health_check(self) -> bool:
        """Ping Redis. Returns False if disconnected or ping fails."""
        if not self._redis:
            return False
        try:
            await self._redis.ping()
            return True
        except Exception:
            return False


cache = RedisCache()
