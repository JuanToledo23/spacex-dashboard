"""Cost analysis and economics endpoint."""

from fastapi import APIRouter

from app.schemas.economics import EconomicsResponse
from app.services.economics_service import get_economics_data

router = APIRouter(prefix="/api/economics", tags=["economics"])


@router.get("", response_model=EconomicsResponse)
async def get_economics():
    return await get_economics_data()
