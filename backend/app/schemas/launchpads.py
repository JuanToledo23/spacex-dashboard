"""Pydantic schemas for launch site data."""

from pydantic import BaseModel


class LaunchpadSummary(BaseModel):
    id: str
    name: str
    full_name: str
    locality: str
    region: str
    latitude: float
    longitude: float
    launch_attempts: int
    launch_successes: int
    status: str
