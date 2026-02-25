"""Per-endpoint rate limiting. Call explicitly on sensitive routes (e.g. /api/chat).

Unlike RateLimitMiddleware (global), this allows per-route limits with custom prefix.
Use for endpoints that need stricter limits than the global 120 req/min.
"""

from __future__ import annotations

from fastapi import HTTPException, Request

from app.cache.redis_cache import cache
from app.utils.client_ip import get_client_ip


async def check_rate_limit(
    request: Request,
    *,
    prefix: str = "rl",
    max_requests: int = 30,
    window_seconds: int = 60,
) -> None:
    """Raise 429 if the caller exceeds max_requests within window_seconds.

    Uses client IP as identifier. Redis counter is shared across workers.
    Different prefixes create separate counters (e.g. rl:chat vs rl:global).
    """
    client_ip = get_client_ip(request)
    key = f"{prefix}:{client_ip}"

    try:
        r = cache._redis  # noqa: SLF001 – internal access is acceptable here
        if r is None:
            return  # Fail open: skip limit when Redis is unavailable

        current = await r.incr(key)
        if current == 1:
            await r.expire(key, window_seconds)

        if current > max_requests:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
            )
    except HTTPException:
        raise
    except Exception:
        pass  # Fail open: never block requests due to Redis errors
