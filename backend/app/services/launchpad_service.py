"""Launch site data service."""

from app.cache.helpers import cached_fetch
from app.clients.spacex_client import spacex_client
from app.config import settings
from app.schemas.launchpads import LaunchpadSummary

CACHE_KEY = "spacex:launchpads"


async def get_launchpads() -> list[LaunchpadSummary]:
    cached = await cached_fetch(CACHE_KEY, settings.launchpads_ttl, _fetch_launchpads)
    return [LaunchpadSummary(**lp) for lp in cached]


async def _fetch_launchpads() -> list[dict]:
    raw = await spacex_client.get_launchpads()
    pads = [
        LaunchpadSummary(
            id=lp["id"],
            name=lp.get("name", ""),
            full_name=lp.get("full_name", ""),
            locality=lp.get("locality", ""),
            region=lp.get("region", ""),
            latitude=lp.get("latitude", 0),
            longitude=lp.get("longitude", 0),
            launch_attempts=lp.get("launch_attempts", 0),
            launch_successes=lp.get("launch_successes", 0),
            status=lp.get("status", "unknown"),
        )
        for lp in raw
    ]
    return [p.model_dump() for p in pads]
