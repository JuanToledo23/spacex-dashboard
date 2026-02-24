"""Individual rocket detail service with engine and stage specs."""

from app.clients.spacex_client import spacex_client
from app.schemas.rockets import (
    EngineSpec,
    PayloadWeight,
    RocketDetail,
    StageSpec,
)
from app.services.launch_service import get_all_launches
from app.utils.calculations import success_rate


def _parse_engine(engines_raw: dict) -> EngineSpec:
    tsl = engines_raw.get("thrust_sea_level") or {}
    tv = engines_raw.get("thrust_vacuum") or {}
    isp = engines_raw.get("isp") or {}
    return EngineSpec(
        number=engines_raw.get("number"),
        type=engines_raw.get("type"),
        version=engines_raw.get("version"),
        propellant_1=engines_raw.get("propellant_1"),
        propellant_2=engines_raw.get("propellant_2"),
        thrust_sea_level_kn=tsl.get("kN"),
        thrust_vacuum_kn=tv.get("kN"),
        isp_sea_level=isp.get("sea_level"),
        isp_vacuum=isp.get("vacuum"),
        thrust_to_weight=engines_raw.get("thrust_to_weight"),
    )


def _parse_stage(stage_raw: dict) -> StageSpec:
    tsl = stage_raw.get("thrust_sea_level") or {}
    tv = stage_raw.get("thrust_vacuum") or {}
    return StageSpec(
        reusable=stage_raw.get("reusable"),
        engines=stage_raw.get("engines"),
        fuel_amount_tons=stage_raw.get("fuel_amount_tons"),
        burn_time_sec=stage_raw.get("burn_time_sec"),
        thrust_sea_level_kn=tsl.get("kN"),
        thrust_vacuum_kn=tv.get("kN"),
    )


async def get_rocket_detail(rocket_id: str) -> RocketDetail:
    rocket = await spacex_client.get_rocket(rocket_id)

    # Count launches for this rocket
    all_launches = await get_all_launches()
    launch_count = sum(1 for lnch in all_launches if lnch.get("rocket") == rocket_id)
    success_count = sum(
        1 for lnch in all_launches if lnch.get("rocket") == rocket_id and lnch.get("success")
    )
    rate = success_rate(success_count, launch_count)

    height = rocket.get("height") or {}
    diameter = rocket.get("diameter") or {}
    mass = rocket.get("mass") or {}
    engines_raw = rocket.get("engines") or {}
    first_stage_raw = rocket.get("first_stage") or {}
    second_stage_raw = rocket.get("second_stage") or {}
    landing_legs = rocket.get("landing_legs") or {}

    payload_weights = [
        PayloadWeight(id=pw["id"], name=pw["name"], kg=pw["kg"], lb=pw["lb"])
        for pw in rocket.get("payload_weights", [])
    ]

    return RocketDetail(
        id=rocket["id"],
        name=rocket.get("name", ""),
        type=rocket.get("type", ""),
        active=rocket.get("active", False),
        stages=rocket.get("stages", 0),
        boosters=rocket.get("boosters", 0),
        cost_per_launch=rocket.get("cost_per_launch"),
        success_rate_pct=rate,
        first_flight=rocket.get("first_flight"),
        country=rocket.get("country"),
        description=rocket.get("description"),
        wikipedia=rocket.get("wikipedia"),
        flickr_images=rocket.get("flickr_images", []),
        height_meters=height.get("meters"),
        diameter_meters=diameter.get("meters"),
        mass_kg=mass.get("kg"),
        engines=_parse_engine(engines_raw) if engines_raw else None,
        payload_weights=payload_weights,
        first_stage=_parse_stage(first_stage_raw) if first_stage_raw else None,
        second_stage=_parse_stage(second_stage_raw) if second_stage_raw else None,
        landing_legs_number=landing_legs.get("number"),
        landing_legs_material=landing_legs.get("material"),
        launch_count=launch_count,
    )
