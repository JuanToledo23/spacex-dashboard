"""AI chat, insights, and fun fact endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.rate_limit import check_rate_limit
from app.config import settings
from app.schemas.ai import AiStatusResponse, ChatRequest, ChatResponse, FunFactResponse
from app.services import ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/status", response_model=AiStatusResponse)
async def ai_status():
    """Check if AI features are available (API key configured)."""
    return AiStatusResponse(available=bool(settings.groq_api_key))


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(req: ChatRequest, request: Request):
    """Send a message to the AI assistant with SpaceX data context."""
    await check_rate_limit(request, prefix="rl:ai", max_requests=20, window_seconds=60)
    history = [{"role": m.role, "content": m.content} for m in req.history]
    response = await ai_service.chat(req.message, history)
    return ChatResponse(response=response)


@router.get("/fun-fact", response_model=FunFactResponse)
async def ai_fun_fact(request: Request):
    """Generate a random fun fact about SpaceX from real data."""
    await check_rate_limit(request, prefix="rl:fact", max_requests=10, window_seconds=60)
    fact = await ai_service.generate_fun_fact()
    if fact is None:
        return JSONResponse(status_code=503, content={"detail": "AI not available"})
    return FunFactResponse(fact=fact)
