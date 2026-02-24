"""Individual launch detail service with payload, crew, and core data."""

import asyncio

from app.cache.redis_cache import cache
from app.clients.spacex_client import spacex_client
from app.schemas.launches import (
    CoreDetail,
    CrewMember,
    LaunchDetail,
    LaunchFailure,
    LaunchLinks,
    PayloadSummary,
)


async def _resolve_rocket_name(rocket_id: str) -> str | None:
    rockets_cached = await cache.get("spacex:rockets")
    if rockets_cached:
        for r in rockets_cached:
            if r["id"] == rocket_id:
                return r["name"]
    try:
        rocket = await spacex_client.get_rocket(rocket_id)
        return rocket.get("name")
    except Exception:
        return None


async def _resolve_launchpad_name(launchpad_id: str) -> str | None:
    cached = await cache.get("spacex:launchpads")
    if cached:
        for lp in cached:
            if lp["id"] == launchpad_id:
                return lp.get("name") or lp.get("full_name")
    try:
        pads = await spacex_client.get_launchpads()
        for lp in pads:
            if lp["id"] == launchpad_id:
                return lp.get("name") or lp.get("full_name")
    except Exception:
        pass
    return None


def _parse_cores(cores_raw: list[dict]) -> list[CoreDetail]:
    result = []
    for c in cores_raw:
        result.append(
            CoreDetail(
                serial=c.get("core"),
                flight=c.get("flight"),
                reused=c.get("reused"),
                landing_attempt=c.get("landing_attempt"),
                landing_success=c.get("landing_success"),
                landing_type=c.get("landing_type"),
            )
        )
    return result


def _parse_links(links_raw: dict) -> LaunchLinks:
    patch = links_raw.get("patch") or {}
    reddit = links_raw.get("reddit") or {}
    flickr = links_raw.get("flickr") or {}
    return LaunchLinks(
        webcast=links_raw.get("webcast"),
        article=links_raw.get("article"),
        wikipedia=links_raw.get("wikipedia"),
        presskit=links_raw.get("presskit"),
        reddit_campaign=reddit.get("campaign"),
        flickr_original=flickr.get("original", []),
        patch_small=patch.get("small"),
        patch_large=patch.get("large"),
    )


def _parse_payloads(payloads_raw: list[dict]) -> list[PayloadSummary]:
    return [
        PayloadSummary(
            id=p["id"],
            name=p.get("name", "Unknown"),
            type=p.get("type"),
            customers=p.get("customers", []),
            mass_kg=p.get("mass_kg"),
            orbit=p.get("orbit"),
            regime=p.get("regime"),
        )
        for p in payloads_raw
    ]


def _parse_crew(crew_raw: list[dict], role_map: dict) -> list[CrewMember]:
    return [
        CrewMember(
            id=c["id"],
            name=c.get("name", "Unknown"),
            agency=c.get("agency"),
            image=c.get("image"),
            role=role_map.get(c["id"]),
        )
        for c in crew_raw
    ]


async def get_launch_detail(launch_id: str) -> LaunchDetail:
    launch = await spacex_client.get_launch(launch_id)

    # Extract crew IDs and roles (v5 crew can be objects with role)
    crew_ids = []
    role_map: dict[str, str] = {}
    for entry in launch.get("crew", []):
        if isinstance(entry, dict):
            cid = entry.get("crew")
            if cid:
                crew_ids.append(cid)
                role_map[cid] = entry.get("role", "")
        elif isinstance(entry, str):
            crew_ids.append(entry)

    payload_ids = launch.get("payloads", [])

    # Fetch related data in parallel
    rocket_name_task = _resolve_rocket_name(launch.get("rocket", ""))
    launchpad_name_task = _resolve_launchpad_name(launch.get("launchpad", ""))
    payloads_task = spacex_client.get_payloads_by_ids(payload_ids)
    crew_task = spacex_client.get_crew_by_ids(crew_ids)

    rocket_name, launchpad_name, payloads_raw, crew_raw = await asyncio.gather(
        rocket_name_task, launchpad_name_task, payloads_task, crew_task
    )

    # Resolve core serials from cached cores
    cores_raw = launch.get("cores", [])
    cores_cached = await cache.get("spacex:cores")
    if cores_cached:
        serial_map = {c["id"]: c.get("serial", c["id"]) for c in cores_cached}
        for core in cores_raw:
            core_id = core.get("core")
            if core_id and core_id in serial_map:
                core["core"] = serial_map[core_id]

    fairings = launch.get("fairings") or {}
    links = launch.get("links") or {}

    return LaunchDetail(
        id=launch["id"],
        flight_number=launch.get("flight_number", 0),
        name=launch.get("name", ""),
        date_utc=launch.get("date_utc", ""),
        success=launch.get("success"),
        upcoming=launch.get("upcoming", False),
        details=launch.get("details"),
        rocket_id=launch.get("rocket", ""),
        rocket_name=rocket_name,
        launchpad_name=launchpad_name,
        cores=_parse_cores(cores_raw),
        payloads=_parse_payloads(payloads_raw),
        crew=_parse_crew(crew_raw, role_map),
        links=_parse_links(links),
        failures=[LaunchFailure(**f) for f in launch.get("failures", [])],
        fairings_recovered=fairings.get("recovered"),
        fairings_reused=fairings.get("reused"),
        static_fire_date_utc=launch.get("static_fire_date_utc"),
    )
