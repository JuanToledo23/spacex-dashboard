"""Landing pad data and statistics service."""

from app.cache.helpers import cached_fetch
from app.clients.spacex_client import spacex_client
from app.config import settings
from app.schemas.landpads import LandingResponse, LandingStats, LandpadSummary
from app.utils.calculations import success_rate

CACHE_KEY = "spacex:landing"


async def get_landing_data() -> LandingResponse:
    cached = await cached_fetch(CACHE_KEY, settings.landing_ttl, _fetch_landing)
    return LandingResponse(**cached) if isinstance(cached, dict) else cached


async def _fetch_landing() -> dict:
    raw = await spacex_client.get_landpads()

    landpads = []
    for lp in raw:
        attempts = lp.get("landing_attempts", 0)
        successes = lp.get("landing_successes", 0)

        landpads.append(
            LandpadSummary(
                id=lp["id"],
                name=lp.get("name", ""),
                full_name=lp.get("full_name", ""),
                type=lp.get("type", ""),
                status=lp.get("status", ""),
                locality=lp.get("locality"),
                region=lp.get("region"),
                latitude=lp.get("latitude", 0),
                longitude=lp.get("longitude", 0),
                landing_attempts=attempts,
                landing_successes=successes,
                success_rate=success_rate(successes, attempts),
            )
        )

    landpads.sort(key=lambda p: p.landing_attempts, reverse=True)

    total_attempts = sum(p.landing_attempts for p in landpads)
    total_successes = sum(p.landing_successes for p in landpads)
    rtls = [p for p in landpads if p.type == "RTLS"]
    asds = [p for p in landpads if p.type == "ASDS"]

    stats = LandingStats(
        total_attempts=total_attempts,
        total_successes=total_successes,
        overall_success_rate=success_rate(total_successes, total_attempts),
        rtls_attempts=sum(p.landing_attempts for p in rtls),
        rtls_successes=sum(p.landing_successes for p in rtls),
        asds_attempts=sum(p.landing_attempts for p in asds),
        asds_successes=sum(p.landing_successes for p in asds),
    )

    response = LandingResponse(stats=stats, landpads=landpads)
    return response.model_dump()
