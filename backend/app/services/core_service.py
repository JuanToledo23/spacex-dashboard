"""Fleet and booster core statistics service."""

from app.cache.helpers import cached_fetch
from app.clients.spacex_client import spacex_client
from app.config import settings
from app.schemas.cores import CoreSummary, FleetStats
from app.utils.calculations import success_rate

CACHE_KEY = "spacex:cores"


async def get_all_cores() -> list[dict]:
    return await cached_fetch(CACHE_KEY, settings.cores_ttl, spacex_client.get_cores)


def _parse_core(core: dict) -> CoreSummary:
    rtls_l = core.get("rtls_landings", 0) or 0
    asds_l = core.get("asds_landings", 0) or 0
    rtls_a = core.get("rtls_attempts", 0) or 0
    asds_a = core.get("asds_attempts", 0) or 0

    return CoreSummary(
        id=core["id"],
        serial=core.get("serial", ""),
        status=core.get("status", "unknown"),
        reuse_count=core.get("reuse_count", 0) or 0,
        rtls_landings=rtls_l,
        rtls_attempts=rtls_a,
        asds_landings=asds_l,
        asds_attempts=asds_a,
        total_landings=rtls_l + asds_l,
        total_attempts=rtls_a + asds_a,
        launches=len(core.get("launches", [])),
    )


async def get_fleet_stats() -> FleetStats:
    cores_raw = await get_all_cores()
    cores = [_parse_core(c) for c in cores_raw]

    active = sum(1 for c in cores if c.status == "active")
    retired = sum(1 for c in cores if c.status in ("retired", "expended"))
    lost = sum(1 for c in cores if c.status == "lost")

    total_landings = sum(c.total_landings for c in cores)
    total_attempts = sum(c.total_attempts for c in cores)

    rtls_l = sum(c.rtls_landings for c in cores)
    rtls_a = sum(c.rtls_attempts for c in cores)
    asds_l = sum(c.asds_landings for c in cores)
    asds_a = sum(c.asds_attempts for c in cores)

    most_reused = sorted(cores, key=lambda c: c.reuse_count, reverse=True)[:10]

    return FleetStats(
        total_cores=len(cores),
        active_cores=active,
        retired_cores=retired,
        lost_cores=lost,
        total_landings=total_landings,
        total_landing_attempts=total_attempts,
        landing_success_rate=success_rate(total_landings, total_attempts),
        rtls_landings=rtls_l,
        rtls_attempts=rtls_a,
        asds_landings=asds_l,
        asds_attempts=asds_a,
        most_reused=most_reused,
    )
