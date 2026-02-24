"""Notification service using Redis Pub/Sub for real-time broadcasting."""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import structlog

from app.cache.redis_cache import cache
from app.schemas.notifications import Notification, NotificationRequest

logger = structlog.get_logger()

CHANNEL = "notifications"


async def publish(req: NotificationRequest) -> Notification:
    """Create a notification and publish it to all connected SSE clients."""
    notification = Notification(
        id=str(uuid.uuid4()),
        type=req.type,
        title=req.title,
        message=req.message,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    payload = notification.model_dump_json()

    if cache._redis:
        try:
            await cache._redis.publish(CHANNEL, payload)
            logger.info(
                "notification_published",
                notification_id=notification.id,
                type=notification.type,
            )
        except Exception:
            logger.warning("notification_publish_failed", reason="redis_error")
    else:
        logger.warning("notification_publish_failed", reason="redis_unavailable")

    return notification


async def subscribe() -> AsyncGenerator[str, None]:
    """Yield SSE-formatted notification events from Redis Pub/Sub."""
    if not cache._redis:
        logger.warning("sse_no_redis", reason="redis not connected")
        return

    try:
        pubsub = cache._redis.pubsub()
        await pubsub.subscribe(CHANNEL)
    except Exception:
        logger.warning("sse_subscribe_failed", reason="redis unreachable")
        return

    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and msg["type"] == "message":
                data = msg["data"]
                yield f"data: {data}\n\n"
            else:
                yield ": heartbeat\n\n"
                await asyncio.sleep(1)
    except Exception:
        logger.warning("sse_connection_lost")
    finally:
        try:
            await pubsub.unsubscribe(CHANNEL)
            await pubsub.close()
        except Exception:
            pass
