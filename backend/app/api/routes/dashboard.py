"""Aggregated dashboard metrics endpoint."""

from fastapi import APIRouter, Request

from app.api.rate_limit import check_rate_limit
from app.schemas.dashboard import DashboardResponse
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(request: Request):
    await check_rate_limit(request, prefix="rl:dash", max_requests=60, window_seconds=60)
    return await dashboard_service.get_dashboard()
