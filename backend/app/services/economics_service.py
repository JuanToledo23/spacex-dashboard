"""Cost analysis and economics data aggregation service."""

import asyncio
from collections import defaultdict

from app.cache.helpers import cached_fetch
from app.cache.redis_cache import cache
from app.clients.spacex_client import spacex_client
from app.config import settings
from app.schemas.economics import (
    AnnualSpend,
    CostByVehicle,
    CustomerVolume,
    EconomicsResponse,
    OrbitMass,
)
from app.services.launch_service import get_all_launches

PAYLOADS_CACHE_KEY = "spacex:payloads"
ECONOMICS_CACHE_KEY = "spacex:economics"


async def _get_all_payloads() -> list[dict]:
    return await cached_fetch(
        PAYLOADS_CACHE_KEY, settings.launches_ttl, spacex_client.get_all_payloads
    )


def _build_cost_by_vehicle(
    rockets: list[dict], launch_counts: dict[str, int]
) -> list[CostByVehicle]:
    results = []
    for r in rockets:
        rid = r["id"]
        count = launch_counts.get(rid, 0)
        cost = r.get("cost_per_launch") or 0
        total = cost * count

        # Find LEO payload weight
        leo_kg = None
        for pw in r.get("payload_weights", []):
            if "low earth" in pw.get("name", "").lower() or pw.get("id") == "leo":
                leo_kg = pw.get("kg")
                break

        cost_per_kg = round(cost / leo_kg, 2) if leo_kg and cost else None

        results.append(
            CostByVehicle(
                rocket_id=rid,
                rocket_name=r.get("name", ""),
                cost_per_launch=cost,
                launches=count,
                total_spend=total,
                payload_kg_leo=leo_kg,
                cost_per_kg_leo=cost_per_kg,
            )
        )

    results.sort(key=lambda x: x.total_spend, reverse=True)
    return results


def _build_annual_spend(launches: list[dict], rocket_cost_map: dict[str, int]) -> list[AnnualSpend]:
    yearly: dict[int, dict] = defaultdict(lambda: {"launches": 0, "spend": 0})

    for launch in launches:
        if launch.get("upcoming"):
            continue
        date = launch.get("date_utc", "")
        if not date:
            continue
        year = int(date[:4])
        rid = launch.get("rocket", "")
        cost = rocket_cost_map.get(rid, 0)
        yearly[year]["launches"] += 1
        yearly[year]["spend"] += cost

    return [
        AnnualSpend(
            year=y,
            launches=d["launches"],
            total_spend=d["spend"],
            avg_cost=round(d["spend"] / d["launches"]) if d["launches"] else 0,
        )
        for y, d in sorted(yearly.items())
    ]


def _build_customers(payloads: list[dict]) -> list[CustomerVolume]:
    customer_data: dict[str, dict] = defaultdict(lambda: {"payloads": 0, "mass": 0.0})
    for p in payloads:
        mass = p.get("mass_kg") or 0
        for c in p.get("customers", []):
            customer_data[c]["payloads"] += 1
            customer_data[c]["mass"] += mass

    results = [
        CustomerVolume(
            customer=c,
            payloads=d["payloads"],
            total_mass_kg=round(d["mass"], 1),
        )
        for c, d in customer_data.items()
    ]
    results.sort(key=lambda x: x.payloads, reverse=True)
    return results[:15]


def _build_orbit_mass(payloads: list[dict]) -> list[OrbitMass]:
    orbit_data: dict[str, dict] = defaultdict(lambda: {"mass": 0.0, "payloads": 0})
    for p in payloads:
        orbit = p.get("orbit") or "Unknown"
        mass = p.get("mass_kg") or 0
        orbit_data[orbit]["mass"] += mass
        orbit_data[orbit]["payloads"] += 1

    results = [
        OrbitMass(
            orbit=o,
            total_mass_kg=round(d["mass"], 1),
            payloads=d["payloads"],
        )
        for o, d in orbit_data.items()
        if d["mass"] > 0
    ]
    results.sort(key=lambda x: x.total_mass_kg, reverse=True)
    return results


async def get_economics_data() -> EconomicsResponse:
    cached = await cache.get(ECONOMICS_CACHE_KEY)
    if cached:
        return EconomicsResponse(**cached)

    # Fetch all data (launches already cached by launch_service)
    launches_raw, rockets_raw, payloads_raw = await asyncio.gather(
        get_all_launches(),
        spacex_client.get_rockets(),
        _get_all_payloads(),
    )

    # Build maps
    rocket_cost_map = {r["id"]: r.get("cost_per_launch") or 0 for r in rockets_raw}
    past_launches = [lnch for lnch in launches_raw if not lnch.get("upcoming")]
    launch_counts: dict[str, int] = defaultdict(int)
    for lnch in past_launches:
        rid = lnch.get("rocket", "")
        if rid:
            launch_counts[rid] += 1

    # Aggregate
    cost_by_vehicle = _build_cost_by_vehicle(rockets_raw, launch_counts)
    annual_spend = _build_annual_spend(launches_raw, rocket_cost_map)
    top_customers = _build_customers(payloads_raw)
    mass_by_orbit = _build_orbit_mass(payloads_raw)

    total_spend = sum(v.total_spend for v in cost_by_vehicle)
    total_launches = len(past_launches)
    total_payloads = len(payloads_raw)
    total_mass = sum((p.get("mass_kg") or 0) for p in payloads_raw)
    avg_cost = round(total_spend / total_launches) if total_launches else 0

    # Find lowest cost per kg
    vehicles_with_cost = [v for v in cost_by_vehicle if v.cost_per_kg_leo]
    lowest = (
        min(vehicles_with_cost, key=lambda v: v.cost_per_kg_leo) if vehicles_with_cost else None
    )

    response = EconomicsResponse(
        total_estimated_spend=total_spend,
        total_launches=total_launches,
        total_payloads=total_payloads,
        total_mass_launched_kg=round(total_mass, 1),
        avg_cost_per_launch=avg_cost,
        lowest_cost_per_kg=lowest.cost_per_kg_leo if lowest else 0,
        lowest_cost_vehicle=lowest.rocket_name if lowest else "",
        cost_by_vehicle=cost_by_vehicle,
        annual_spend=annual_spend,
        top_customers=top_customers,
        mass_by_orbit=mass_by_orbit,
    )

    await cache.set(ECONOMICS_CACHE_KEY, response.model_dump(), settings.economics_ttl)
    return response
