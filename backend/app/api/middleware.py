"""Request tracing middleware, global rate limiting, and error handler.

Flow: Request → RateLimitMiddleware → TraceMiddleware → Route → Response
All middleware runs on every request; error_handler catches unhandled exceptions.
"""

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.cache.redis_cache import cache
from app.utils.client_ip import get_client_ip

logger = structlog.get_logger()

# Global rate limit: max requests per IP per window (applies to all /api/*)
GLOBAL_RATE_LIMIT = 120
GLOBAL_RATE_WINDOW = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Global rate limiter applied to all /api/ endpoints. Uses Redis counter per IP."""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for non-API routes
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = get_client_ip(request)
        key = f"rl:global:{client_ip}"

        try:
            r = cache._redis  # noqa: SLF001
            if r is not None:
                current = await r.incr(key)
                if current == 1:
                    await r.expire(key, GLOBAL_RATE_WINDOW)
                if current > GLOBAL_RATE_LIMIT:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many requests. Please try again later."},
                    )
        except Exception:
            pass  # Fail open: allow requests if Redis is down

        return await call_next(request)


class TraceMiddleware(BaseHTTPMiddleware):
    """Assigns trace ID to each request and logs method, path, status, duration."""

    async def dispatch(self, request: Request, call_next):
        # Reuse client-provided trace ID or generate new one
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request.state.trace_id = trace_id

        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)

        response.headers["X-Trace-ID"] = trace_id

        logger.info(
            "request_completed",
            trace_id=trace_id,
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response


async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler. Returns structured JSON with trace_id for debugging."""
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))

    from app.clients.spacex_client import SpaceXAPIError

    if isinstance(exc, SpaceXAPIError):
        status = 502 if exc.status_code >= 500 else exc.status_code
        code = "SPACEX_API_ERROR"
    else:
        status = 500
        code = "INTERNAL_ERROR"

    logger.error("unhandled_exception", trace_id=trace_id, error=str(exc))

    return JSONResponse(
        status_code=status,
        content={"code": code, "message": str(exc), "trace_id": trace_id},
    )
