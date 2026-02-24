"""Fleet / booster core statistics endpoint."""

from fastapi import APIRouter

from app.schemas.cores import FleetStats
from app.services import core_service

router = APIRouter(prefix="/api/cores", tags=["cores"])


@router.get("/stats", response_model=FleetStats)
async def fleet_stats():
    return await core_service.get_fleet_stats()
