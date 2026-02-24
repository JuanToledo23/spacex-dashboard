"""Health check endpoint for Redis connectivity."""

from fastapi import APIRouter

from app.cache.redis_cache import cache

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    redis_ok = await cache.health_check()
    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected",
    }
