"""Pydantic schemas for the aggregated dashboard response."""

from pydantic import BaseModel

from app.schemas.launchpads import LaunchpadSummary


class Insight(BaseModel):
    id: str
    type: str  # "summary" | "metric" | "ai_summary" | "action"
    text: str
    payload: dict | None = None
    action_type: str | None = None  # "optimize" | "investigate" | "scale" | "reduce" | "monitor"
    priority: str | None = None  # "high" | "medium" | "low"
    domains: list[str] = []  # e.g. ["fleet", "emissions"]


class LaunchHighlight(BaseModel):
    id: str
    name: str
    date_utc: str
    success: bool | None = None
    upcoming: bool
    rocket_name: str | None = None
    details: str | None = None
    patch_small: str | None = None
    webcast: str | None = None
    flickr_images: list[str] = []


class DashboardResponse(BaseModel):
    total_rockets: int
    active_rockets: int
    total_launches: int
    successful_launches: int
    failed_launches: int
    upcoming_launches: int
    success_rate: float
    launches_by_year: list[dict]
    launches_by_rocket: list[dict]
    launches_by_site: list[dict]
    total_starlink: int
    active_cores: int
    total_landings: int
    latest_launch: LaunchHighlight | None
    next_launch: LaunchHighlight | None
    recent_launches: list[LaunchHighlight]
    insights: list[Insight]
    launchpads: list[LaunchpadSummary] = []
