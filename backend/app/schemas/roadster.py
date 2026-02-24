"""Pydantic schemas for Tesla Roadster telemetry."""

from pydantic import BaseModel


class RoadsterData(BaseModel):
    name: str
    launch_date_utc: str
    speed_kph: float
    earth_distance_km: float
    earth_distance_mi: float
    mars_distance_km: float
    mars_distance_mi: float
    orbit_type: str
    period_days: float
    apoapsis_au: float
    periapsis_au: float
    semi_major_axis_au: float | None = None
    eccentricity: float | None = None
    inclination: float | None = None
    details: str | None = None
    wikipedia: str | None = None
    video: str | None = None
    flickr_images: list[str] = []
