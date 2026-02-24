"""Real-time notification endpoints (send + SSE stream)."""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.api.rate_limit import check_rate_limit
from app.schemas.notifications import NotificationRequest, NotificationSentResponse
from app.services import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post("/send", response_model=NotificationSentResponse)
async def send_notification(req: NotificationRequest, request: Request):
    """Publish a notification to all connected SSE clients."""
    await check_rate_limit(request, prefix="rl:notif", max_requests=30, window_seconds=60)
    notification = await notification_service.publish(req)
    return NotificationSentResponse(ok=True, notification=notification)


@router.get("/stream")
async def notification_stream():
    """SSE endpoint — clients connect via EventSource to receive notifications."""
    return StreamingResponse(
        notification_service.subscribe(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
