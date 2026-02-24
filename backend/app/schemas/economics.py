"""Pydantic schemas for economics and cost analysis data."""

from pydantic import BaseModel


class CostByVehicle(BaseModel):
    rocket_id: str
    rocket_name: str
    cost_per_launch: int
    launches: int
    total_spend: int
    payload_kg_leo: float | None = None
    cost_per_kg_leo: float | None = None


class AnnualSpend(BaseModel):
    year: int
    launches: int
    total_spend: int
    avg_cost: float


class CustomerVolume(BaseModel):
    customer: str
    payloads: int
    total_mass_kg: float


class OrbitMass(BaseModel):
    orbit: str
    total_mass_kg: float
    payloads: int


class EconomicsResponse(BaseModel):
    total_estimated_spend: int
    total_launches: int
    total_payloads: int
    total_mass_launched_kg: float
    avg_cost_per_launch: float
    lowest_cost_per_kg: float
    lowest_cost_vehicle: str
    cost_by_vehicle: list[CostByVehicle]
    annual_spend: list[AnnualSpend]
    top_customers: list[CustomerVolume]
    mass_by_orbit: list[OrbitMass]
