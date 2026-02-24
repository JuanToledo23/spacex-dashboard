"""Launch site listing endpoint."""

from fastapi import APIRouter

from app.schemas.launchpads import LaunchpadSummary
from app.services import launchpad_service

router = APIRouter(prefix="/api/launchpads", tags=["launchpads"])


@router.get("", response_model=list[LaunchpadSummary])
async def list_launchpads():
    return await launchpad_service.get_launchpads()
