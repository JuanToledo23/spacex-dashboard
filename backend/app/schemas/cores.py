"""Pydantic schemas for fleet and booster core data."""

from pydantic import BaseModel


class CoreSummary(BaseModel):
    id: str
    serial: str
    status: str
    reuse_count: int
    rtls_landings: int
    rtls_attempts: int
    asds_landings: int
    asds_attempts: int
    total_landings: int
    total_attempts: int
    launches: int


class FleetStats(BaseModel):
    total_cores: int
    active_cores: int
    retired_cores: int
    lost_cores: int
    total_landings: int
    total_landing_attempts: int
    landing_success_rate: float
    rtls_landings: int
    rtls_attempts: int
    asds_landings: int
    asds_attempts: int
    most_reused: list[CoreSummary]
