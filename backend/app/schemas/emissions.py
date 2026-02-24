"""Pydantic schemas for emissions estimation data."""

from pydantic import BaseModel


class EmissionsByVehicle(BaseModel):
    rocket_id: str
    rocket_name: str
    fuel_type: str
    fuel_per_launch_tonnes: float
    co2_per_launch_tonnes: float
    launches: int
    total_co2_tonnes: float
    payload_kg_leo: float | None = None
    co2_per_kg_leo: float | None = None


class AnnualEmissions(BaseModel):
    year: int
    launches: int
    co2_tonnes: float
    fuel_burned_tonnes: float
    reuse_savings_tonnes: float


class FuelBreakdown(BaseModel):
    fuel_type: str
    fuel_tonnes: float
    co2_tonnes: float
    percentage: float


class EmissionsResponse(BaseModel):
    total_co2_tonnes: float
    total_fuel_tonnes: float
    co2_per_launch: float
    reuse_co2_saved_tonnes: float
    total_reuses: int
    total_launches: int
    emissions_by_vehicle: list[EmissionsByVehicle]
    annual_emissions: list[AnnualEmissions]
    fuel_breakdown: list[FuelBreakdown]
