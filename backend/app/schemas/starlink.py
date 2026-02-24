"""Pydantic schemas for Starlink satellite data."""

from pydantic import BaseModel


class StarlinkSatellite(BaseModel):
    id: str
    object_name: str | None = None
    version: str | None = None
    height_km: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    velocity_kms: float | None = None
    launch_id: str | None = None


class StarlinkPosition(BaseModel):
    id: str
    object_name: str | None = None
    latitude: float
    longitude: float
    height_km: float | None = None
    velocity_kms: float | None = None
    version: str | None = None
