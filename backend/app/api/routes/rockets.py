"""Rocket listing and detail endpoints."""

from fastapi import APIRouter, HTTPException

from app.clients.spacex_client import SpaceXAPIError
from app.schemas.rockets import RocketDetail, RocketSummary
from app.services import rocket_service
from app.services.rocket_detail_service import get_rocket_detail

router = APIRouter(prefix="/api/rockets", tags=["rockets"])


@router.get("", response_model=list[RocketSummary])
async def list_rockets():
    return await rocket_service.get_rockets()


@router.get("/{rocket_id}", response_model=RocketDetail)
async def get_rocket(rocket_id: str):
    try:
        return await get_rocket_detail(rocket_id)
    except SpaceXAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
