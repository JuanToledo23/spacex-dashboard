"""Tesla Roadster / Starman telemetry service."""

from app.cache.helpers import cached_fetch
from app.clients.spacex_client import spacex_client
from app.config import settings
from app.schemas.roadster import RoadsterData

CACHE_KEY = "spacex:roadster"


async def get_roadster_data() -> RoadsterData:
    cached = await cached_fetch(CACHE_KEY, settings.roadster_ttl, _fetch_roadster)
    return RoadsterData(**cached) if isinstance(cached, dict) else cached


async def _fetch_roadster() -> dict:
    raw = await spacex_client.get_roadster()

    data = RoadsterData(
        name=raw.get("name", ""),
        launch_date_utc=raw.get("launch_date_utc", ""),
        speed_kph=raw.get("speed_kph", 0),
        earth_distance_km=raw.get("earth_distance_km", 0),
        earth_distance_mi=raw.get("earth_distance_mi", 0),
        mars_distance_km=raw.get("mars_distance_km", 0),
        mars_distance_mi=raw.get("mars_distance_mi", 0),
        orbit_type=raw.get("orbit_type", ""),
        period_days=raw.get("period_days", 0),
        apoapsis_au=raw.get("apoapsis_au", 0),
        periapsis_au=raw.get("periapsis_au", 0),
        semi_major_axis_au=raw.get("semi_major_axis_au"),
        eccentricity=raw.get("eccentricity"),
        inclination=raw.get("inclination"),
        details=raw.get("details"),
        wikipedia=raw.get("wikipedia"),
        video=raw.get("video"),
        flickr_images=raw.get("flickr_images", []),
    )

    return data.model_dump()
