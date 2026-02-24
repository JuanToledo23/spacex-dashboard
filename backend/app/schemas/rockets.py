"""Pydantic schemas for rocket listing and detail data."""

from pydantic import BaseModel


class RocketSummary(BaseModel):
    id: str
    name: str
    type: str
    active: bool
    success_rate_pct: float
    launch_count: int
    cost_per_launch: int | None = None
    first_flight: str | None = None
    description: str | None = None
    flickr_images: list[str] = []
    height_meters: float | None = None
    diameter_meters: float | None = None
    mass_kg: float | None = None


# --- Detail schemas ---


class EngineSpec(BaseModel):
    number: int | None = None
    type: str | None = None
    version: str | None = None
    propellant_1: str | None = None
    propellant_2: str | None = None
    thrust_sea_level_kn: float | None = None
    thrust_vacuum_kn: float | None = None
    isp_sea_level: float | None = None
    isp_vacuum: float | None = None
    thrust_to_weight: float | None = None


class PayloadWeight(BaseModel):
    id: str
    name: str
    kg: float
    lb: float


class StageSpec(BaseModel):
    reusable: bool | None = None
    engines: int | None = None
    fuel_amount_tons: float | None = None
    burn_time_sec: float | None = None
    thrust_sea_level_kn: float | None = None
    thrust_vacuum_kn: float | None = None


class RocketDetail(BaseModel):
    id: str
    name: str
    type: str
    active: bool
    stages: int
    boosters: int
    cost_per_launch: int | None = None
    success_rate_pct: float
    first_flight: str | None = None
    country: str | None = None
    description: str | None = None
    wikipedia: str | None = None
    flickr_images: list[str] = []
    height_meters: float | None = None
    diameter_meters: float | None = None
    mass_kg: float | None = None
    engines: EngineSpec | None = None
    payload_weights: list[PayloadWeight] = []
    first_stage: StageSpec | None = None
    second_stage: StageSpec | None = None
    landing_legs_number: int | None = None
    landing_legs_material: str | None = None
    launch_count: int = 0
