"""Landing pad data endpoint."""

from fastapi import APIRouter

from app.schemas.landpads import LandingResponse
from app.services.landing_service import get_landing_data

router = APIRouter(prefix="/api/landing", tags=["landing"])


@router.get("", response_model=LandingResponse)
async def get_landing():
    return await get_landing_data()
