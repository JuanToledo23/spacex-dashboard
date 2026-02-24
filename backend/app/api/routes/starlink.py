"""Starlink satellite data endpoints."""

from fastapi import APIRouter, Query

from app.schemas.common import PaginatedResponse
from app.schemas.starlink import StarlinkPosition, StarlinkSatellite
from app.services import starlink_service

router = APIRouter(prefix="/api/starlink", tags=["starlink"])


@router.get("", response_model=PaginatedResponse[StarlinkSatellite])
async def list_starlink(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    version: str | None = None,
):
    items, total = await starlink_service.get_starlink(page=page, limit=limit, version=version)
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.get("/positions", response_model=list[StarlinkPosition])
async def starlink_positions():
    return await starlink_service.get_starlink_positions()


@router.get("/stats")
async def starlink_stats():
    return await starlink_service.get_starlink_stats()
