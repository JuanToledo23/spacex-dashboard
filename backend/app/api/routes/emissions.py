"""Emissions estimation endpoint."""

from fastapi import APIRouter

from app.schemas.emissions import EmissionsResponse
from app.services.emissions_service import get_emissions_data

router = APIRouter(prefix="/api/emissions", tags=["emissions"])


@router.get("", response_model=EmissionsResponse)
async def get_emissions():
    return await get_emissions_data()
