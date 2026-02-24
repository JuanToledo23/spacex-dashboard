"""Estimate launch emissions (CO2) from SpaceX rocket fuel data.

Emission factors (documented sources):
- RP-1/LOX: O/F ratio ~2.27, RP-1 fraction ~30.6% of propellant mass,
  CO2 per kg RP-1 burned: ~3.15 kg (NASA, ESA literature).
- Liquid Methane/LOX: O/F ratio ~3.6, CH4 fraction ~21.7%,
  CO2 per kg methane: ~2.75 kg.
- Reuse manufacturing savings: ~60 tonnes CO2 per booster avoided
  (conservative estimate from industry lifecycle analyses).
"""

import asyncio
from collections import defaultdict

from app.cache.redis_cache import cache
from app.clients.spacex_client import spacex_client
from app.config import settings
from app.schemas.emissions import (
    AnnualEmissions,
    EmissionsByVehicle,
    EmissionsResponse,
    FuelBreakdown,
)
from app.services.launch_service import get_all_launches

EMISSIONS_CACHE_KEY = "spacex:emissions"

# Emission factors
RP1_FUEL_FRACTION = 0.306  # RP-1 mass fraction in RP-1/LOX propellant
RP1_CO2_PER_KG = 3.15  # kg CO2 per kg RP-1 burned
METHANE_FUEL_FRACTION = 0.217  # CH4 mass fraction in CH4/LOX propellant
METHANE_CO2_PER_KG = 2.75  # kg CO2 per kg CH4 burned
REUSE_SAVINGS_TONNES = 60.0  # estimated CO2 saved per reuse (manufacturing)


def _classify_fuel(rocket: dict) -> str:
    """Determine fuel type from rocket engine data."""
    engines = rocket.get("engines", {})
    prop2 = (engines.get("propellant_2") or "").lower()
    if "methane" in prop2:
        return "liquid_methane"
    return "rp1"


def _calc_fuel_tonnes(rocket: dict) -> float:
    """Total propellant per launch in tonnes."""
    first = rocket.get("first_stage", {}).get("fuel_amount_tons") or 0
    second = rocket.get("second_stage", {}).get("fuel_amount_tons") or 0
    boosters = rocket.get("boosters", 0)

    # Falcon Heavy has 2 side boosters + center core = 3x first stage
    if boosters >= 2:
        total = first * (boosters + 1) + second
    else:
        total = first + second

    return round(total, 2)


def _calc_co2_tonnes(fuel_tonnes: float, fuel_type: str) -> float:
    """Estimate CO2 from propellant mass and fuel type."""
    fuel_kg = fuel_tonnes * 1000

    if fuel_type == "liquid_methane":
        fuel_burned = fuel_kg * METHANE_FUEL_FRACTION
        co2 = fuel_burned * METHANE_CO2_PER_KG
    else:
        fuel_burned = fuel_kg * RP1_FUEL_FRACTION
        co2 = fuel_burned * RP1_CO2_PER_KG

    return round(co2 / 1000, 2)  # return in tonnes


def _get_leo_capacity(rocket: dict) -> float | None:
    """Get LEO payload capacity in kg."""
    for pw in rocket.get("payload_weights", []):
        if "low earth" in pw.get("name", "").lower() or pw.get("id") == "leo":
            return pw.get("kg")
    return None


async def get_emissions_data() -> EmissionsResponse:
    cached = await cache.get(EMISSIONS_CACHE_KEY)
    if cached:
        return EmissionsResponse(**cached)

    launches_raw, rockets_raw = await asyncio.gather(
        get_all_launches(),
        spacex_client.get_rockets(),
    )

    # Build rocket lookup
    rocket_map = {r["id"]: r for r in rockets_raw}

    # Pre-compute per-rocket values
    rocket_fuel: dict[str, float] = {}
    rocket_fuel_type: dict[str, str] = {}
    rocket_co2: dict[str, float] = {}
    for r in rockets_raw:
        rid = r["id"]
        ft = _classify_fuel(r)
        fuel = _calc_fuel_tonnes(r)
        rocket_fuel[rid] = fuel
        rocket_fuel_type[rid] = ft
        rocket_co2[rid] = _calc_co2_tonnes(fuel, ft)

    # Process launches
    past_launches = [lnch for lnch in launches_raw if not lnch.get("upcoming")]

    total_co2 = 0.0
    total_fuel = 0.0
    total_reuses = 0
    launch_counts: dict[str, int] = defaultdict(int)
    yearly: dict[int, dict] = defaultdict(
        lambda: {"launches": 0, "co2": 0.0, "fuel": 0.0, "reuse_savings": 0.0}
    )
    fuel_totals: dict[str, dict] = defaultdict(lambda: {"fuel": 0.0, "co2": 0.0})

    for launch in past_launches:
        rid = launch.get("rocket", "")
        if rid not in rocket_map:
            continue

        date = launch.get("date_utc", "")
        if not date:
            continue

        year = int(date[:4])
        fuel = rocket_fuel.get(rid, 0)
        co2 = rocket_co2.get(rid, 0)
        ft = rocket_fuel_type.get(rid, "rp1")

        total_co2 += co2
        total_fuel += fuel
        launch_counts[rid] += 1

        # Count reused cores
        reuses_in_launch = sum(1 for c in launch.get("cores", []) if c.get("reused"))
        total_reuses += reuses_in_launch
        reuse_saving = reuses_in_launch * REUSE_SAVINGS_TONNES

        yearly[year]["launches"] += 1
        yearly[year]["co2"] += co2
        yearly[year]["fuel"] += fuel
        yearly[year]["reuse_savings"] += reuse_saving

        fuel_totals[ft]["fuel"] += fuel
        fuel_totals[ft]["co2"] += co2

    total_launches = len(past_launches)
    reuse_co2_saved = total_reuses * REUSE_SAVINGS_TONNES

    # Emissions by vehicle
    emissions_by_vehicle = []
    for r in rockets_raw:
        rid = r["id"]
        count = launch_counts.get(rid, 0)
        if count == 0:
            continue
        ft = rocket_fuel_type[rid]
        fuel_per = rocket_fuel[rid]
        co2_per = rocket_co2[rid]
        leo_kg = _get_leo_capacity(r)
        co2_per_kg = round((co2_per * 1000) / leo_kg, 2) if leo_kg and co2_per else None

        emissions_by_vehicle.append(
            EmissionsByVehicle(
                rocket_id=rid,
                rocket_name=r.get("name", ""),
                fuel_type="Liquid Methane" if ft == "liquid_methane" else "RP-1 Kerosene",
                fuel_per_launch_tonnes=fuel_per,
                co2_per_launch_tonnes=co2_per,
                launches=count,
                total_co2_tonnes=round(co2_per * count, 2),
                payload_kg_leo=leo_kg,
                co2_per_kg_leo=co2_per_kg,
            )
        )
    emissions_by_vehicle.sort(key=lambda x: x.total_co2_tonnes, reverse=True)

    # Annual emissions
    annual_emissions = [
        AnnualEmissions(
            year=y,
            launches=d["launches"],
            co2_tonnes=round(d["co2"], 2),
            fuel_burned_tonnes=round(d["fuel"], 2),
            reuse_savings_tonnes=round(d["reuse_savings"], 2),
        )
        for y, d in sorted(yearly.items())
    ]

    # Fuel breakdown
    total_fuel_all = sum(d["fuel"] for d in fuel_totals.values()) or 1
    fuel_breakdown = []
    label_map = {"rp1": "RP-1 Kerosene", "liquid_methane": "Liquid Methane"}
    for ft, d in fuel_totals.items():
        fuel_breakdown.append(
            FuelBreakdown(
                fuel_type=label_map.get(ft, ft),
                fuel_tonnes=round(d["fuel"], 2),
                co2_tonnes=round(d["co2"], 2),
                percentage=round(d["fuel"] / total_fuel_all * 100, 1),
            )
        )
    fuel_breakdown.sort(key=lambda x: x.fuel_tonnes, reverse=True)

    response = EmissionsResponse(
        total_co2_tonnes=round(total_co2, 2),
        total_fuel_tonnes=round(total_fuel, 2),
        co2_per_launch=round(total_co2 / total_launches, 2) if total_launches else 0,
        reuse_co2_saved_tonnes=round(reuse_co2_saved, 2),
        total_reuses=total_reuses,
        total_launches=total_launches,
        emissions_by_vehicle=emissions_by_vehicle,
        annual_emissions=annual_emissions,
        fuel_breakdown=fuel_breakdown,
    )

    await cache.set(EMISSIONS_CACHE_KEY, response.model_dump(), settings.emissions_ttl)
    return response
