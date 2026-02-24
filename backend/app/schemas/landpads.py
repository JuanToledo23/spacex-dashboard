"""Pydantic schemas for landing pad data."""

from pydantic import BaseModel


class LandpadSummary(BaseModel):
    id: str
    name: str
    full_name: str
    type: str
    status: str
    locality: str | None = None
    region: str | None = None
    latitude: float
    longitude: float
    landing_attempts: int
    landing_successes: int
    success_rate: float


class LandingStats(BaseModel):
    total_attempts: int
    total_successes: int
    overall_success_rate: float
    rtls_attempts: int
    rtls_successes: int
    asds_attempts: int
    asds_successes: int


class LandingResponse(BaseModel):
    stats: LandingStats
    landpads: list[LandpadSummary]
