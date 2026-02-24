"""Launch listing, filtering, pagination, and yearly aggregation service."""

from collections import defaultdict

from app.cache.helpers import cached_fetch
from app.cache.redis_cache import cache
from app.clients.spacex_client import spacex_client
from app.config import settings
from app.schemas.launches import LaunchAggregate, LaunchSummary

CACHE_KEY = "spacex:launches"


async def get_all_launches() -> list[dict]:
    return await cached_fetch(CACHE_KEY, settings.launches_ttl, spacex_client.get_launches)


def _parse_launch(launch: dict, rocket_map: dict | None = None) -> LaunchSummary:
    rocket_id = launch.get("rocket", "")
    links = launch.get("links") or {}
    patch = links.get("patch") or {}
    return LaunchSummary(
        id=launch["id"],
        name=launch.get("name", ""),
        date_utc=launch.get("date_utc", ""),
        success=launch.get("success"),
        upcoming=launch.get("upcoming", False),
        rocket_id=rocket_id,
        rocket_name=rocket_map.get(rocket_id) if rocket_map else None,
        details=launch.get("details"),
        patch_small=patch.get("small"),
    )


async def get_launches(
    page: int = 1,
    limit: int = 20,
    success: bool | None = None,
    upcoming: bool | None = None,
    rocket_id: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    sort: str = "date_utc",
    order: str = "desc",
) -> tuple[list[LaunchSummary], int]:
    all_launches = await get_all_launches()

    rocket_map: dict[str, str] = {}
    rockets_cached = await cache.get("spacex:rockets")
    if rockets_cached:
        rocket_map = {r["id"]: r["name"] for r in rockets_cached}

    filtered = all_launches
    if success is not None:
        filtered = [item for item in filtered if item.get("success") == success]
    if upcoming is not None:
        filtered = [item for item in filtered if item.get("upcoming") == upcoming]
    if rocket_id:
        filtered = [item for item in filtered if item.get("rocket") == rocket_id]
    if from_date:
        filtered = [item for item in filtered if item.get("date_utc", "") >= from_date]
    if to_date:
        filtered = [item for item in filtered if item.get("date_utc", "") <= to_date]

    reverse = order == "desc"
    filtered.sort(key=lambda x: x.get(sort, ""), reverse=reverse)

    total = len(filtered)
    start = (page - 1) * limit
    page_items = filtered[start : start + limit]

    launches = [_parse_launch(item, rocket_map) for item in page_items]
    return launches, total


async def get_launches_by_year() -> list[LaunchAggregate]:
    all_launches = await get_all_launches()

    year_data: dict[int, dict] = defaultdict(lambda: {"total": 0, "successes": 0, "failures": 0})
    for launch in all_launches:
        date = launch.get("date_utc", "")
        if not date or launch.get("upcoming"):
            continue
        year = int(date[:4])
        year_data[year]["total"] += 1
        if launch.get("success") is True:
            year_data[year]["successes"] += 1
        elif launch.get("success") is False:
            year_data[year]["failures"] += 1

    return [
        LaunchAggregate(year=y, total=d["total"], successes=d["successes"], failures=d["failures"])
        for y, d in sorted(year_data.items())
    ]
