"""AI service for LLM-powered insights, chat, and fun facts using Groq."""

import json

import structlog
from groq import AsyncGroq

from app.config import settings
from app.schemas.dashboard import Insight
from app.services import (
    core_service,
    economics_service,
    emissions_service,
    history_service,
    landing_service,
    launch_service,
    launchpad_service,
    roadster_service,
    rocket_service,
    starlink_service,
)
from app.utils.calculations import success_rate as calc_success_rate

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are a SpaceX data analyst embedded in a dashboard application.
You have access to comprehensive SpaceX program data provided below, including:
missions, rockets, fleet/booster reuse, Starlink satellites, launch sites, landing pads,
economics (cost analysis), emissions (environmental impact), historical milestones,
and the Tesla Roadster (Starman) in orbit.
Answer questions accurately based on the data. Be concise, professional, and specific.
Use numbers and percentages when relevant. If the data doesn't contain the answer, say so.
Do not make up information. Respond in the same language the user writes in.
Keep responses under 200 words unless a detailed comparison is requested.

Formatting rules:
- Use **bold** for key numbers and names.
- Separate paragraphs with a blank line.
- Use bullet lists (- item) when comparing or listing multiple items.
- Use numbered lists (1. item) for sequential steps or rankings.
- Keep paragraphs short (2-3 sentences max)."""

INSIGHTS_PROMPT = """You are a SpaceX operations strategist for a dashboard called QuadSci \
("Orchestrating Intelligence"). Based on the comprehensive program data, generate exactly 5 \
actionable recommendations. Each must:
1. Cross-reference at least 2 data domains \
(missions, fleet, economics, emissions, starlink, landing)
2. Propose a specific action with expected impact using real numbers
3. Be 1-2 sentences, concise and data-driven

Valid action_type: "optimize", "investigate", "scale", "reduce", "monitor"
Valid priority: "high", "medium", "low"
Valid domain: "missions", "fleet", "economics", "emissions", "starlink", "landing"

Return ONLY a JSON array of 5 objects, no other text. Example:
[{"text":"Rec here.","action_type":"optimize",\
"priority":"high","domains":["fleet","emissions"]}]"""


def _is_available() -> bool:
    return bool(settings.groq_api_key)


def _get_client() -> AsyncGroq:
    return AsyncGroq(api_key=settings.groq_api_key)


async def _build_data_context() -> str:
    """Gather all SpaceX data from cache into a compact text summary for the LLM."""
    rockets = await rocket_service.get_rockets()
    all_launches = await launch_service.get_all_launches()
    starlink_stats = await starlink_service.get_starlink_stats()
    fleet = await core_service.get_fleet_stats()

    total = len(all_launches)
    successful = sum(1 for lnch in all_launches if lnch.get("success") is True)
    failed = sum(1 for lnch in all_launches if lnch.get("success") is False)
    upcoming = sum(1 for lnch in all_launches if lnch.get("upcoming"))
    rate = calc_success_rate(successful, successful + failed)

    rocket_lines = [
        f"  - {r.name}: {r.launch_count} launches,"
        f" {r.success_rate_pct}% success,"
        f" {'active' if r.active else 'retired'}"
        for r in rockets
    ]

    by_year = await launch_service.get_launches_by_year()
    year_lines = [
        f"  - {y.year}: {y.total} launches ({y.successes} ok, {y.failures} failed)" for y in by_year
    ]

    sections = [
        f"""== Missions ==
- Total: {total} ({successful} successful, {failed} failed, {upcoming} upcoming)
- Success rate: {rate}%
Launches by year:
{chr(10).join(year_lines)}""",
        f"""== Fleet ==
- Active boosters: {fleet.active_cores}
- Total landings: {fleet.total_landings}
- Landing success rate: {fleet.landing_success_rate}%""",
        f"""== Starlink ==
- Total satellites tracked: {starlink_stats["total"]}""",
        f"""== Rockets ==
{chr(10).join(rocket_lines)}""",
    ]

    # Emissions
    try:
        emissions = await emissions_service.get_emissions_data()
        vehicle_lines = [
            f"  - {v.rocket_name}: {v.total_co2_tonnes:.0f} t CO2"
            f" ({v.launches} launches, fuel: {v.fuel_type})"
            for v in emissions.emissions_by_vehicle
        ]
        annual_em_lines = [
            f"  - {a.year}: {a.co2_tonnes:,.0f} t CO2, {a.launches} launches,"
            f" fuel: {a.fuel_burned_tonnes:,.0f} t, reuse saved: {a.reuse_savings_tonnes:,.0f} t"
            for a in emissions.annual_emissions
        ]
        fuel_lines = [
            f"  - {f.fuel_type}: {f.co2_tonnes:,.0f} t CO2 ({f.percentage:.1f}%)"
            for f in emissions.fuel_breakdown
        ]
        reuse_saved = emissions.reuse_co2_saved_tonnes
        reuse_count = emissions.total_reuses
        sections.append(f"""== Emissions (estimated) ==
- Total CO2: {emissions.total_co2_tonnes:,.0f} tonnes
- Total fuel: {emissions.total_fuel_tonnes:,.0f} tonnes
- Avg CO2/launch: {emissions.co2_per_launch:,.0f} tonnes
- Reuse savings: {reuse_saved:,.0f} t CO2 ({reuse_count} reuses)
By vehicle:
{chr(10).join(vehicle_lines)}
Annual emissions by year:
{chr(10).join(annual_em_lines)}
Fuel breakdown:
{chr(10).join(fuel_lines)}""")
    except Exception as exc:
        logger.debug("context_emissions_skipped", error=str(exc))

    # Economics
    try:
        economics = await economics_service.get_economics_data()
        cost_lines = [
            f"  - {v.rocket_name}: ${v.cost_per_launch:,}/launch,"
            f" {v.launches} launches, ${v.total_spend:,} total"
            for v in economics.cost_by_vehicle
        ]
        annual_spend_lines = [
            f"  - {a.year}: ${a.total_spend:,} ({a.launches} launches, avg ${a.avg_cost:,.0f})"
            for a in economics.annual_spend
        ]
        customer_lines = [
            f"  - {c.customer}: {c.payloads} payloads, {c.total_mass_kg:,.0f} kg"
            for c in economics.top_customers[:10]
        ]
        orbit_lines = [
            f"  - {o.orbit}: {o.total_mass_kg:,.0f} kg ({o.payloads} payloads)"
            for o in economics.mass_by_orbit
        ]
        low_kg = economics.lowest_cost_per_kg
        low_v = economics.lowest_cost_vehicle
        sections.append(f"""== Economics (estimated) ==
- Total spend: ${economics.total_estimated_spend:,}
- Avg cost/launch: ${economics.avg_cost_per_launch:,.0f}
- Lowest cost/kg LEO: ${low_kg:,.0f}/kg ({low_v})
- Total payloads: {economics.total_payloads}
- Mass launched: {economics.total_mass_launched_kg:,.0f} kg
By vehicle:
{chr(10).join(cost_lines)}
Annual spend by year:
{chr(10).join(annual_spend_lines)}
Top customers:
{chr(10).join(customer_lines)}
Mass by target orbit:
{chr(10).join(orbit_lines)}""")
    except Exception as exc:
        logger.debug("context_economics_skipped", error=str(exc))

    # History
    try:
        history = await history_service.get_history()
        event_lines = [f"  - {e.event_date_utc[:10]}: {e.title}" for e in history.events[-15:]]
        sections.append(f"""== History (last {len(event_lines)} of {history.total} milestones) ==
{chr(10).join(event_lines)}""")
    except Exception as exc:
        logger.debug("context_history_skipped", error=str(exc))

    # Landing pads
    try:
        landing = await landing_service.get_landing_data()
        stats = landing.stats
        pad_lines = [
            f"  - {p.full_name} ({p.type}, {p.status}):"
            f" {p.landing_successes}/{p.landing_attempts}"
            f" landings, {p.success_rate}% success"
            for p in landing.landpads[:8]
        ]
        rtls = f"{stats.rtls_successes}/{stats.rtls_attempts}"
        asds = f"{stats.asds_successes}/{stats.asds_attempts}"
        sections.append(f"""== Landing Operations ==
- Attempts: {stats.total_attempts}, ok: {stats.total_successes}\
, rate: {stats.overall_success_rate}%
- RTLS: {rtls} | ASDS (droneship): {asds}
Pads:
{chr(10).join(pad_lines)}""")
    except Exception as exc:
        logger.debug("context_landing_skipped", error=str(exc))

    # Launchpads (launch sites)
    try:
        launchpads = await launchpad_service.get_launchpads()
        lp_lines = [
            f"  - {lp.full_name} ({lp.locality},"
            f" {lp.region}):"
            f" {lp.launch_successes}/{lp.launch_attempts}"
            f" launches, status: {lp.status}"
            for lp in launchpads
        ]
        sections.append(f"""== Launch Sites ==
{chr(10).join(lp_lines)}""")
    except Exception as exc:
        logger.debug("context_launchpads_skipped", error=str(exc))

    # Roadster / Starman
    try:
        roadster = await roadster_service.get_roadster_data()
        sections.append(f"""== Starman / Tesla Roadster ==
- Launched: {roadster.launch_date_utc[:10]}
- Current speed: {roadster.speed_kph:,.0f} km/h
- Distance from Earth: {roadster.earth_distance_km:,.0f} km
- Distance from Mars: {roadster.mars_distance_km:,.0f} km
- Orbit type: {roadster.orbit_type}
- Orbital period: {roadster.period_days:.1f} days
- Apoapsis: {roadster.apoapsis_au:.3f} AU | Periapsis: {roadster.periapsis_au:.3f} AU""")
    except Exception as exc:
        logger.debug("context_roadster_skipped", error=str(exc))

    return "SpaceX Program Data\n\n" + "\n\n".join(sections)


VALID_ACTION_TYPES = {"optimize", "investigate", "scale", "reduce", "monitor"}
VALID_PRIORITIES = {"high", "medium", "low"}
VALID_DOMAINS = {"missions", "fleet", "economics", "emissions", "starlink", "landing"}


async def generate_ai_insights() -> list[Insight] | None:
    """Generate AI-powered actionable recommendations. Returns None if unavailable."""
    if not _is_available():
        return None

    data_context = await _build_data_context()

    try:
        client = _get_client()
        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": INSIGHTS_PROMPT},
                {"role": "user", "content": data_context},
            ],
            temperature=0.7,
            max_tokens=900,
        )

        raw = response.choices[0].message.content or "[]"
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        items = json.loads(raw)
        if not isinstance(items, list) or len(items) == 0:
            return None

        insights = []
        for i, item in enumerate(items[:5]):
            if isinstance(item, str):
                text = item
                action_type = "monitor"
                priority = "medium"
                domains: list[str] = []
            elif isinstance(item, dict):
                text = str(item.get("text", ""))
                action_type = item.get("action_type", "monitor")
                priority = item.get("priority", "medium")
                domains = item.get("domains", [])
            else:
                continue

            if not text:
                continue
            if action_type not in VALID_ACTION_TYPES:
                action_type = "monitor"
            if priority not in VALID_PRIORITIES:
                priority = "medium"
            domains = [d for d in domains if d in VALID_DOMAINS][:3]

            insights.append(
                Insight(
                    id=f"ai_action_{i + 1}",
                    type="ai_summary",
                    text=text,
                    action_type=action_type,
                    priority=priority,
                    domains=domains,
                )
            )
        return insights if insights else None

    except Exception as exc:
        logger.warning("ai_insights_failed", error=str(exc))
        return None


FUN_FACT_PROMPT = """You are a SpaceX trivia expert. Based on the data provided, generate ONE short,
surprising fun fact. It must be specific with real numbers from the data.
Maximum 25 words. Write it as a single sentence, no quotes, no prefix.
Respond in the same language as the user's locale or default to English.
Vary the topic each time: pick randomly from missions, rockets, costs, emissions, landings,
Starlink, Starman/Roadster, or historical milestones."""


async def generate_fun_fact() -> str | None:
    """Generate a single short fun fact from SpaceX data. Returns None if unavailable."""
    if not _is_available():
        return None

    data_context = await _build_data_context()

    try:
        client = _get_client()
        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": FUN_FACT_PROMPT},
                {"role": "user", "content": data_context},
            ],
            temperature=0.95,
            max_tokens=80,
        )
        fact = (response.choices[0].message.content or "").strip().strip("\"'")
        return fact if fact else None
    except Exception as exc:
        logger.warning("ai_fun_fact_failed", error=str(exc))
        return None


async def chat(message: str, history: list[dict]) -> str:
    """Process a chat message with SpaceX data context."""
    if not _is_available():
        return (
            "AI assistant is not configured. Set the"
            " GROQ_API_KEY environment variable to enable"
            " this feature."
        )

    data_context = await _build_data_context()

    messages: list[dict] = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{data_context}"},
    ]

    # Include recent conversation history (last 6 exchanges max)
    for msg in history[-12:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})

    try:
        client = _get_client()
        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content or "I couldn't generate a response."
    except Exception as exc:
        logger.warning("ai_chat_failed", error=str(exc))
        return "Sorry, I'm having trouble connecting right now. Please try again in a moment."
