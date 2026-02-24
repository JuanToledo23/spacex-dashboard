"""Tesla Roadster / Starman telemetry endpoint."""

from fastapi import APIRouter

from app.schemas.roadster import RoadsterData
from app.services.roadster_service import get_roadster_data

router = APIRouter(prefix="/api/roadster", tags=["roadster"])


@router.get("", response_model=RoadsterData)
async def get_roadster():
    return await get_roadster_data()
