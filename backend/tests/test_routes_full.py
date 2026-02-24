"""Integration tests for all API route endpoints."""

from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.cores import FleetStats
from app.schemas.dashboard import DashboardResponse, Insight
from app.schemas.economics import EconomicsResponse
from app.schemas.emissions import EmissionsResponse
from app.schemas.history import HistoryResponse
from app.schemas.landpads import LandingResponse, LandingStats
from app.schemas.launches import LaunchDetail, LaunchLinks
from app.schemas.roadster import RoadsterData
from app.schemas.rockets import RocketDetail


@pytest.mark.asyncio
async def test_get_rockets(client):
    with patch(
        "app.services.rocket_service.get_rockets",
        new_callable=AsyncMock,
        return_value=[],
    ):
        resp = await client.get("/api/rockets")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.asyncio
async def test_get_rocket_detail(client):
    detail = RocketDetail(
        id="r1",
        name="Falcon 9",
        type="rocket",
        active=True,
        stages=2,
        boosters=0,
        success_rate_pct=98.0,
        launch_count=100,
    )
    with patch(
        "app.api.routes.rockets.get_rocket_detail",
        new_callable=AsyncMock,
        return_value=detail,
    ):
        resp = await client.get("/api/rockets/r1")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Falcon 9"


@pytest.mark.asyncio
async def test_get_rocket_not_found(client):
    from app.clients.spacex_client import SpaceXAPIError

    with patch(
        "app.api.routes.rockets.get_rocket_detail",
        new_callable=AsyncMock,
        side_effect=SpaceXAPIError(404, "Not found"),
    ):
        resp = await client.get("/api/rockets/bad")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_launches(client):
    with patch(
        "app.services.launch_service.get_launches",
        new_callable=AsyncMock,
        return_value=([], 0),
    ):
        resp = await client.get("/api/launches")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0


@pytest.mark.asyncio
async def test_launches_invalid_date(client):
    resp = await client.get("/api/launches?from_date=not-a-date")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_launches_invalid_sort(client):
    resp = await client.get("/api/launches?sort=hacked_field")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_launch_detail(client):
    detail = LaunchDetail(
        id="l1",
        flight_number=100,
        name="CRS-25",
        date_utc="2023-07-14",
        success=True,
        upcoming=False,
        rocket_id="r1",
        links=LaunchLinks(),
    )
    with patch(
        "app.api.routes.launches.get_launch_detail",
        new_callable=AsyncMock,
        return_value=detail,
    ):
        resp = await client.get("/api/launches/l1")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_starlink(client):
    with patch(
        "app.services.starlink_service.get_starlink",
        new_callable=AsyncMock,
        return_value=([], 0),
    ):
        resp = await client.get("/api/starlink")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_starlink_positions(client):
    with patch(
        "app.services.starlink_service.get_starlink_positions",
        new_callable=AsyncMock,
        return_value=[],
    ):
        resp = await client.get("/api/starlink/positions")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_starlink_stats(client):
    with patch(
        "app.services.starlink_service.get_starlink_stats",
        new_callable=AsyncMock,
        return_value={"total": 5000, "by_version": [], "avg_height_km": 550},
    ):
        resp = await client.get("/api/starlink/stats")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_fleet_stats(client):
    stats = FleetStats(
        total_cores=10,
        active_cores=5,
        retired_cores=3,
        lost_cores=2,
        total_landings=100,
        total_landing_attempts=110,
        landing_success_rate=90.9,
        rtls_landings=30,
        rtls_attempts=33,
        asds_landings=70,
        asds_attempts=77,
        most_reused=[],
    )
    with patch(
        "app.services.core_service.get_fleet_stats",
        new_callable=AsyncMock,
        return_value=stats,
    ):
        resp = await client.get("/api/cores/stats")
        assert resp.status_code == 200
        assert resp.json()["total_cores"] == 10


@pytest.mark.asyncio
async def test_list_launchpads(client):
    with patch(
        "app.services.launchpad_service.get_launchpads",
        new_callable=AsyncMock,
        return_value=[],
    ):
        resp = await client.get("/api/launchpads")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_history(client):
    history = HistoryResponse(events=[], total=0)
    with patch(
        "app.api.routes.history.get_history",
        new_callable=AsyncMock,
        return_value=history,
    ):
        resp = await client.get("/api/history")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_get_landing(client):
    landing = LandingResponse(
        stats=LandingStats(
            total_attempts=0,
            total_successes=0,
            overall_success_rate=0,
            rtls_attempts=0,
            rtls_successes=0,
            asds_attempts=0,
            asds_successes=0,
        ),
        landpads=[],
    )
    with patch(
        "app.api.routes.landing.get_landing_data",
        new_callable=AsyncMock,
        return_value=landing,
    ):
        resp = await client.get("/api/landing")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_roadster(client):
    roadster = RoadsterData(
        name="Tesla",
        launch_date_utc="2018-02-06",
        speed_kph=9521,
        earth_distance_km=300e6,
        earth_distance_mi=186e6,
        mars_distance_km=150e6,
        mars_distance_mi=93e6,
        orbit_type="heliocentric",
        period_days=557,
        apoapsis_au=1.664,
        periapsis_au=0.986,
    )
    with patch(
        "app.api.routes.roadster.get_roadster_data",
        new_callable=AsyncMock,
        return_value=roadster,
    ):
        resp = await client.get("/api/roadster")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Tesla"


@pytest.mark.asyncio
async def test_get_emissions(client):
    emissions = EmissionsResponse(
        total_co2_tonnes=100,
        total_fuel_tonnes=200,
        co2_per_launch=50,
        reuse_co2_saved_tonnes=60,
        total_reuses=1,
        total_launches=2,
        emissions_by_vehicle=[],
        annual_emissions=[],
        fuel_breakdown=[],
    )
    with patch(
        "app.api.routes.emissions.get_emissions_data",
        new_callable=AsyncMock,
        return_value=emissions,
    ):
        resp = await client.get("/api/emissions")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_economics(client):
    economics = EconomicsResponse(
        total_estimated_spend=1000000000,
        total_launches=200,
        total_payloads=100,
        total_mass_launched_kg=1000000,
        avg_cost_per_launch=50000000,
        lowest_cost_per_kg=2700,
        lowest_cost_vehicle="Falcon 9",
        cost_by_vehicle=[],
        annual_spend=[],
        top_customers=[],
        mass_by_orbit=[],
    )
    with patch(
        "app.api.routes.economics.get_economics_data",
        new_callable=AsyncMock,
        return_value=economics,
    ):
        resp = await client.get("/api/economics")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_endpoint(client):
    dashboard = DashboardResponse(
        total_rockets=4,
        active_rockets=2,
        total_launches=200,
        successful_launches=180,
        failed_launches=5,
        upcoming_launches=15,
        success_rate=97.3,
        launches_by_year=[],
        launches_by_rocket=[],
        launches_by_site=[],
        total_starlink=5000,
        active_cores=10,
        total_landings=200,
        latest_launch=None,
        next_launch=None,
        recent_launches=[],
        insights=[Insight(id="i1", type="summary", text="Test insight")],
    )
    with patch(
        "app.services.dashboard_service.get_dashboard",
        new_callable=AsyncMock,
        return_value=dashboard,
    ):
        resp = await client.get("/api/dashboard")
        assert resp.status_code == 200
        assert resp.json()["total_rockets"] == 4


@pytest.mark.asyncio
async def test_ai_status(client):
    with patch("app.api.routes.ai.settings") as mock_settings:
        mock_settings.groq_api_key = "test-key"
        resp = await client.get("/api/ai/status")
        assert resp.status_code == 200
        assert resp.json()["available"] is True


@pytest.mark.asyncio
async def test_ai_fun_fact(client):
    with patch(
        "app.services.ai_service.generate_fun_fact",
        new_callable=AsyncMock,
        return_value="Fun fact here",
    ):
        resp = await client.get("/api/ai/fun-fact")
        assert resp.status_code == 200
        assert resp.json()["fact"] == "Fun fact here"


@pytest.mark.asyncio
async def test_ai_fun_fact_unavailable(client):
    with patch(
        "app.services.ai_service.generate_fun_fact",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.get("/api/ai/fun-fact")
        assert resp.status_code == 503


@pytest.mark.asyncio
async def test_ai_chat(client):
    with patch(
        "app.services.ai_service.chat",
        new_callable=AsyncMock,
        return_value="Hello from AI",
    ):
        resp = await client.post(
            "/api/ai/chat",
            json={"message": "hi", "history": []},
        )
        assert resp.status_code == 200
        assert resp.json()["response"] == "Hello from AI"


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
