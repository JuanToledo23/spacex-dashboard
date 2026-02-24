"""Dashboard aggregation service combining data from all SpaceX sources."""

from app.clients.spacex_client import spacex_client
from app.schemas.cores import FleetStats
from app.schemas.dashboard import DashboardResponse, Insight, LaunchHighlight
from app.schemas.rockets import RocketSummary
from app.services import (
    ai_service,
    core_service,
    launch_service,
    launchpad_service,
    rocket_service,
    starlink_service,
)
from app.utils.calculations import success_rate as calc_success_rate


def _build_launch_highlight(raw: dict, rocket_map: dict) -> LaunchHighlight:
    links = raw.get("links") or {}
    patch = links.get("patch") or {}
    flickr = links.get("flickr") or {}
    return LaunchHighlight(
        id=raw["id"],
        name=raw.get("name", ""),
        date_utc=raw.get("date_utc", ""),
        success=raw.get("success"),
        upcoming=raw.get("upcoming", False),
        rocket_name=rocket_map.get(raw.get("rocket", "")),
        details=raw.get("details"),
        patch_small=patch.get("small"),
        webcast=links.get("webcast"),
        flickr_images=flickr.get("original", []) or [],
    )


async def get_dashboard() -> DashboardResponse:
    rockets = await rocket_service.get_rockets()
    launches_by_year = await launch_service.get_launches_by_year()
    all_launches = await launch_service.get_all_launches()
    starlink_stats = await starlink_service.get_starlink_stats()
    fleet = await core_service.get_fleet_stats()
    pads = await launchpad_service.get_launchpads()

    rocket_name_map = {r.id: r.name for r in rockets}

    total_launches = len(all_launches)
    successful = sum(1 for lnch in all_launches if lnch.get("success") is True)
    failed = sum(1 for lnch in all_launches if lnch.get("success") is False)
    upcoming = sum(1 for lnch in all_launches if lnch.get("upcoming"))
    decided = successful + failed
    success_rate = calc_success_rate(successful, decided)

    # Launches by rocket
    rocket_launch_counts: dict[str, int] = {}
    for launch in all_launches:
        rid = launch.get("rocket", "")
        name = rocket_name_map.get(rid, rid)
        rocket_launch_counts[name] = rocket_launch_counts.get(name, 0) + 1

    launches_by_rocket = [
        {"rocket": name, "count": count}
        for name, count in sorted(rocket_launch_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    # Launches by site
    pad_name_map = {p.id: p.name for p in pads}
    site_counts: dict[str, int] = {}
    for launch in all_launches:
        pid = launch.get("launchpad", "")
        name = pad_name_map.get(pid, pid[:8])
        site_counts[name] = site_counts.get(name, 0) + 1

    launches_by_site = [
        {"site": name, "count": count}
        for name, count in sorted(site_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    # Latest and next launch
    try:
        latest_raw = await spacex_client.get_latest_launch()
        latest_launch = _build_launch_highlight(latest_raw, rocket_name_map)
    except Exception:
        latest_launch = None

    try:
        next_raw = await spacex_client.get_next_launch()
        next_launch = _build_launch_highlight(next_raw, rocket_name_map)
    except Exception:
        next_launch = None

    # Recent launches (last 8 past launches)
    past = [lnch for lnch in all_launches if not lnch.get("upcoming")]
    past_sorted = sorted(past, key=lambda x: x.get("date_utc", ""), reverse=True)[:12]
    recent_launches = [_build_launch_highlight(lnch, rocket_name_map) for lnch in past_sorted]

    # Try AI-generated actionable recommendations, fall back to deterministic
    insights = await ai_service.generate_ai_insights()
    if insights is None:
        insights = _generate_insights(
            rockets, successful, failed, total_launches, upcoming, starlink_stats, fleet
        )

    return DashboardResponse(
        total_rockets=len(rockets),
        active_rockets=sum(1 for r in rockets if r.active),
        total_launches=total_launches,
        successful_launches=successful,
        failed_launches=failed,
        upcoming_launches=upcoming,
        success_rate=success_rate,
        launches_by_year=[a.model_dump() for a in launches_by_year],
        launches_by_rocket=launches_by_rocket,
        launches_by_site=launches_by_site,
        total_starlink=starlink_stats["total"],
        active_cores=fleet.active_cores,
        total_landings=fleet.total_landings,
        latest_launch=latest_launch,
        next_launch=next_launch,
        recent_launches=recent_launches,
        insights=insights,
        launchpads=pads,
    )


def _generate_insights(
    rockets: list[RocketSummary],
    successful: int,
    failed: int,
    total: int,
    upcoming: int,
    starlink_stats: dict,
    fleet: FleetStats,
) -> list[Insight]:
    """Deterministic cross-domain actionable recommendations."""
    insights: list[Insight] = []

    active_rockets = [r for r in rockets if r.active and r.launch_count > 0]
    if active_rockets:
        best = max(active_rockets, key=lambda r: r.success_rate_pct)
        savings_per_reuse = 50  # ~$50M per booster reuse
        est_savings = fleet.total_landings * savings_per_reuse
        insights.append(
            Insight(
                id="fleet_economics",
                type="action",
                text=(
                    f"{best.name} at {best.success_rate_pct}% success across"
                    f" {best.launch_count} missions — prioritize its booster rotation to"
                    f" maximize the ~${est_savings}M already saved through"
                    f" {fleet.total_landings} recoveries."
                ),
                action_type="optimize",
                priority="high",
                domains=["fleet", "economics"],
            )
        )

    if fleet.landing_success_rate < 100:
        gap = 100 - fleet.landing_success_rate
        insights.append(
            Insight(
                id="landing_improvement",
                type="action",
                text=(
                    f"Landing success rate is {fleet.landing_success_rate}%"
                    f" ({fleet.total_landings} landings)."
                    f" Closing the {gap:.1f}% gap could save additional boosters"
                    f" worth ~$50M each, reducing both cost and manufacturing emissions."
                ),
                action_type="investigate",
                priority="high" if gap > 5 else "medium",
                domains=["landing", "economics", "emissions"],
            )
        )

    if upcoming > 0:
        insights.append(
            Insight(
                id="scale_manifest",
                type="action",
                text=(
                    f"{upcoming} missions in manifest with {fleet.active_cores}"
                    f" active boosters. Monitor fleet utilization — at current cadence"
                    f" (~{total} total missions), scaling launch sites and pad turnaround"
                    f" is key to sustaining growth."
                ),
                action_type="scale",
                priority="high" if upcoming > 10 else "medium",
                domains=["missions", "fleet"],
            )
        )

    if fleet.total_landings > 0:
        reuse_ratio = fleet.total_landings / max(1, total)
        co2_per_launch_est = 425  # tonnes avg estimate
        saved_tonnes = int(fleet.total_landings * co2_per_launch_est * 0.3)
        insights.append(
            Insight(
                id="emissions_reuse",
                type="action",
                text=(
                    f"Booster reuse rate of {reuse_ratio:.0%} has prevented an estimated"
                    f" {saved_tonnes:,} tonnes of CO₂. Increasing recovery rate from"
                    f" {fleet.landing_success_rate}% toward 98% would amplify savings"
                    f" on every future launch."
                ),
                action_type="reduce",
                priority="medium",
                domains=["emissions", "fleet"],
            )
        )

    sat_total = starlink_stats.get("total", 0)
    if sat_total > 0:
        avg_h = starlink_stats.get("avg_height_km", 550)
        insights.append(
            Insight(
                id="starlink_coverage",
                type="action",
                text=(
                    f"Starlink constellation at ~{sat_total:,} satellites"
                    f" (avg {avg_h:.0f} km altitude). Monitor orbital density and"
                    f" coordinate launch cadence to optimize coverage expansion"
                    f" while managing per-launch cost of ~$67M per Falcon 9 mission."
                ),
                action_type="monitor",
                priority="medium",
                domains=["starlink", "economics", "missions"],
            )
        )

    return insights
