"""Rocket listing service with launch count enrichment."""

from app.cache.helpers import cached_fetch
from app.clients.spacex_client import spacex_client
from app.config import settings
from app.schemas.rockets import RocketSummary
from app.utils.calculations import success_rate

CACHE_KEY = "spacex:rockets"


async def get_rockets() -> list[RocketSummary]:
    cached = await cached_fetch(CACHE_KEY, settings.rockets_ttl, _fetch_rockets)
    return [RocketSummary(**r) for r in cached]


async def _fetch_rockets() -> list[dict]:
    rockets_raw = await spacex_client.get_rockets()
    launches_raw = await spacex_client.get_launches()

    launch_counts: dict[str, int] = {}
    success_counts: dict[str, int] = {}
    for launch in launches_raw:
        rid = launch.get("rocket")
        if not rid:
            continue
        launch_counts[rid] = launch_counts.get(rid, 0) + 1
        if launch.get("success"):
            success_counts[rid] = success_counts.get(rid, 0) + 1

    rockets = []
    for r in rockets_raw:
        rid = r["id"]
        total = launch_counts.get(rid, 0)
        successes = success_counts.get(rid, 0)

        height = r.get("height") or {}
        diameter = r.get("diameter") or {}
        mass = r.get("mass") or {}

        rockets.append(
            RocketSummary(
                id=rid,
                name=r.get("name", ""),
                type=r.get("type", ""),
                active=r.get("active", False),
                success_rate_pct=success_rate(successes, total),
                launch_count=total,
                cost_per_launch=r.get("cost_per_launch"),
                first_flight=r.get("first_flight"),
                description=r.get("description"),
                flickr_images=r.get("flickr_images", []),
                height_meters=height.get("meters"),
                diameter_meters=diameter.get("meters"),
                mass_kg=mass.get("kg"),
            )
        )

    return [r.model_dump() for r in rockets]
