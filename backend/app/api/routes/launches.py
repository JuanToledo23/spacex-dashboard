"""Launch listing and detail endpoints."""

import re
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.clients.spacex_client import SpaceXAPIError
from app.schemas.common import PaginatedResponse
from app.schemas.launches import LaunchDetail, LaunchSummary
from app.services import launch_service
from app.services.launch_detail_service import get_launch_detail

router = APIRouter(prefix="/api/launches", tags=["launches"])

ALLOWED_SORT_FIELDS = {"date_utc", "name", "success"}
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def _validate_date(value: str | None, name: str) -> None:
    if value is not None and not ISO_DATE_RE.match(value):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid {name}: expected ISO-8601 date (YYYY-MM-DD…)",
        )


@router.get("", response_model=PaginatedResponse[LaunchSummary])
async def list_launches(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    success: bool | None = None,
    upcoming: bool | None = None,
    rocket_id: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    sort: str = Query("date_utc"),
    order: Literal["asc", "desc"] = "desc",
):
    _validate_date(from_date, "from_date")
    _validate_date(to_date, "to_date")

    if sort not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid sort field. Allowed: {', '.join(sorted(ALLOWED_SORT_FIELDS))}",
        )

    items, total = await launch_service.get_launches(
        page=page,
        limit=limit,
        success=success,
        upcoming=upcoming,
        rocket_id=rocket_id,
        from_date=from_date,
        to_date=to_date,
        sort=sort,
        order=order,
    )
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.get("/{launch_id}", response_model=LaunchDetail)
async def get_launch(launch_id: str):
    try:
        return await get_launch_detail(launch_id)
    except SpaceXAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
