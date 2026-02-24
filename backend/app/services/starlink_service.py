"""Starlink satellite data, positions, and statistics service."""

from app.cache.helpers import cached_fetch
from app.clients.spacex_client import spacex_client
from app.config import settings
from app.schemas.starlink import StarlinkPosition, StarlinkSatellite

CACHE_KEY = "spacex:starlink"


async def _fetch_starlink() -> list[dict]:
    all_sats: list[dict] = []
    page = 1
    while True:
        result = await spacex_client.query_starlink(query={}, options={"page": page, "limit": 500})
        docs = result.get("docs", [])
        all_sats.extend(docs)
        if not result.get("hasNextPage", False):
            break
        page += 1
    return all_sats


async def get_all_starlink() -> list[dict]:
    return await cached_fetch(CACHE_KEY, settings.starlink_ttl, _fetch_starlink)


def _parse_satellite(sat: dict) -> StarlinkSatellite:
    spacetrack = sat.get("spaceTrack") or {}
    height = sat.get("height_km") or spacetrack.get("APOAPSIS")

    return StarlinkSatellite(
        id=sat["id"],
        object_name=spacetrack.get("OBJECT_NAME"),
        version=sat.get("version"),
        height_km=round(float(height), 2) if height else None,
        latitude=sat.get("latitude"),
        longitude=sat.get("longitude"),
        velocity_kms=sat.get("velocity_kms"),
        launch_id=sat.get("launch"),
    )


async def get_starlink(
    page: int = 1,
    limit: int = 20,
    version: str | None = None,
) -> tuple[list[StarlinkSatellite], int]:
    all_sats = await get_all_starlink()

    filtered = all_sats
    if version:
        filtered = [s for s in filtered if s.get("version") == version]

    total = len(filtered)
    start = (page - 1) * limit
    page_items = filtered[start : start + limit]

    satellites = [_parse_satellite(s) for s in page_items]
    return satellites, total


async def get_starlink_positions() -> list[StarlinkPosition]:
    all_sats = await get_all_starlink()
    positions: list[StarlinkPosition] = []
    for sat in all_sats:
        lat = sat.get("latitude")
        lng = sat.get("longitude")
        if lat is None or lng is None:
            continue
        spacetrack = sat.get("spaceTrack") or {}
        height = sat.get("height_km") or spacetrack.get("APOAPSIS")
        vel = sat.get("velocity_kms")
        positions.append(
            StarlinkPosition(
                id=sat["id"],
                object_name=spacetrack.get("OBJECT_NAME"),
                latitude=lat,
                longitude=lng,
                height_km=round(float(height), 2) if height else None,
                velocity_kms=round(float(vel), 2) if vel else None,
                version=sat.get("version"),
            )
        )
    return positions


async def get_starlink_stats() -> dict:
    all_sats = await get_all_starlink()

    version_counts: dict[str, int] = {}
    heights: list[float] = []
    for sat in all_sats:
        v = sat.get("version") or "unknown"
        version_counts[v] = version_counts.get(v, 0) + 1

        spacetrack = sat.get("spaceTrack") or {}
        height = sat.get("height_km") or spacetrack.get("APOAPSIS")
        if height:
            heights.append(float(height))

    return {
        "total": len(all_sats),
        "by_version": [{"version": v, "count": c} for v, c in sorted(version_counts.items())],
        "avg_height_km": round(sum(heights) / len(heights), 2) if heights else 0,
    }
