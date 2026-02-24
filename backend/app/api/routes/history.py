"""Historical milestones endpoint."""

from fastapi import APIRouter

from app.schemas.history import HistoryResponse
from app.services.history_service import get_history

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryResponse)
async def list_history():
    return await get_history()
