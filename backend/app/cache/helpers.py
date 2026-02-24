"""Cache-aside helper with stampede prevention via distributed Redis locks.

Flow: 1) Check cache → 2) If miss, try lock → 3) Fetch, cache, release lock.
Prevents multiple workers from hitting the upstream API when cache expires.
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from app.cache.redis_cache import cache


async def cached_fetch(
    key: str,
    ttl: int,
    fetch_fn: Callable[[], Awaitable[Any]],
) -> Any:
    """Return cached data or fetch via fetch_fn, then cache. Uses lock to avoid stampede."""
    # 1) Cache hit: return immediately
    cached_data = await cache.get(key)
    if cached_data is not None:
        return cached_data

    # 2) Cache miss: try to acquire lock. If another worker has it, wait and retry cache
    if not await cache.acquire_lock(key):
        await asyncio.sleep(1)
        cached_data = await cache.get(key)
        if cached_data is not None:
            return cached_data

    # 3) We hold the lock: fetch from upstream, cache, then release
    try:
        result = await fetch_fn()
        await cache.set(key, result, ttl)
        return result
    finally:
        await cache.release_lock(key)
