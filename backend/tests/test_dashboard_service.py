"""Tests for the dashboard service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.dashboard_service import _build_launch_highlight, _generate_insights


class TestBuildLaunchHighlight:
    def test_full_launch(self):
        raw = {
            "id": "l1",
            "name": "Starlink 6-1",
            "date_utc": "2023-07-01T00:00:00Z",
            "success": True,
            "upcoming": False,
            "rocket": "r1",
            "details": "Group 6",
            "links": {
                "patch": {"small": "s.png"},
                "webcast": "https://yt.com",
                "flickr": {"original": ["img.jpg"]},
            },
        }
        rocket_map = {"r1": "Falcon 9"}
        result = _build_launch_highlight(raw, rocket_map)
        assert result.name == "Starlink 6-1"
        assert result.rocket_name == "Falcon 9"
        assert result.patch_small == "s.png"
        assert result.flickr_images == ["img.jpg"]

    def test_missing_links(self):
        raw = {"id": "l2", "name": "Test", "rocket": "r1"}
        result = _build_launch_highlight(raw, {})
        assert result.patch_small is None
        assert result.webcast is None
        assert result.flickr_images == []


class TestGenerateInsights:
    def test_generates_insights(self):
        rockets = [
            MagicMock(
                id="r1",
                name="Falcon 9",
                active=True,
                launch_count=100,
                success_rate_pct=98.0,
            ),
        ]
        fleet = MagicMock(
            total_landings=200,
            landing_success_rate=95.0,
        )
        starlink_stats = {"total": 5000, "avg_height_km": 550}

        result = _generate_insights(rockets, 180, 5, 200, 15, starlink_stats, fleet)
        assert len(result) >= 4
        ids = [i.id for i in result]
        assert "fleet_economics" in ids
        assert "landing_improvement" in ids
        assert "scale_manifest" in ids
        assert "emissions_reuse" in ids
        assert "starlink_coverage" in ids
        for ins in result:
            assert ins.action_type is not None
            assert ins.priority is not None
            assert len(ins.domains) >= 2

    def test_no_upcoming(self):
        rockets = [
            MagicMock(
                id="r1",
                name="Falcon 9",
                active=True,
                launch_count=10,
                success_rate_pct=90.0,
            ),
        ]
        fleet = MagicMock(total_landings=0, landing_success_rate=0.0)
        starlink = {"total": 100, "avg_height_km": 550}

        result = _generate_insights(rockets, 9, 1, 10, 0, starlink, fleet)
        ids = [i.id for i in result]
        assert "scale_manifest" not in ids
        assert "emissions_reuse" not in ids

    def test_no_active_rockets(self):
        rockets = [
            MagicMock(
                id="r1",
                name="Falcon 1",
                active=False,
                launch_count=5,
                success_rate_pct=40.0,
            ),
        ]
        fleet = MagicMock(total_landings=0, landing_success_rate=0.0)
        starlink = {"total": 0, "avg_height_km": 0}

        result = _generate_insights(rockets, 2, 3, 5, 0, starlink, fleet)
        ids = [i.id for i in result]
        assert "fleet_economics" not in ids


class TestGetDashboard:
    @pytest.mark.asyncio
    async def test_full_dashboard(self):
        from app.schemas.launches import LaunchAggregate
        from app.schemas.launchpads import LaunchpadSummary
        from app.schemas.rockets import RocketSummary

        rockets = [
            RocketSummary(
                id="r1",
                name="Falcon 9",
                type="rocket",
                active=True,
                launch_count=100,
                success_rate_pct=98.0,
            ),
        ]
        launches = [
            {
                "id": "l1",
                "success": True,
                "upcoming": False,
                "rocket": "r1",
                "date_utc": "2023-01-01T00:00:00Z",
                "launchpad": "lp1",
                "links": {},
            },
        ]
        starlink_stats = {"total": 5000, "avg_height_km": 550}
        fleet = MagicMock(active_cores=10, total_landings=200, landing_success_rate=95.0)
        pads = [
            LaunchpadSummary(
                id="lp1",
                name="LC-39A",
                full_name="LC-39A",
                locality="Florida",
                region="US",
                latitude=28.6,
                longitude=-80.6,
                launch_attempts=50,
                launch_successes=49,
                status="active",
            ),
        ]
        by_year = [LaunchAggregate(year=2023, total=1, successes=1, failures=0)]

        with (
            patch(
                "app.services.dashboard_service.rocket_service.get_rockets",
                new_callable=AsyncMock,
                return_value=rockets,
            ),
            patch(
                "app.services.dashboard_service.launch_service.get_launches_by_year",
                new_callable=AsyncMock,
                return_value=by_year,
            ),
            patch(
                "app.services.dashboard_service.launch_service.get_all_launches",
                new_callable=AsyncMock,
                return_value=launches,
            ),
            patch(
                "app.services.dashboard_service.starlink_service.get_starlink_stats",
                new_callable=AsyncMock,
                return_value=starlink_stats,
            ),
            patch(
                "app.services.dashboard_service.core_service.get_fleet_stats",
                new_callable=AsyncMock,
                return_value=fleet,
            ),
            patch(
                "app.services.dashboard_service.launchpad_service.get_launchpads",
                new_callable=AsyncMock,
                return_value=pads,
            ),
            patch(
                "app.services.dashboard_service.spacex_client.get_latest_launch",
                new_callable=AsyncMock,
                return_value={
                    "id": "latest",
                    "name": "Latest",
                    "rocket": "r1",
                    "links": {},
                },
            ),
            patch(
                "app.services.dashboard_service.spacex_client.get_next_launch",
                new_callable=AsyncMock,
                return_value={
                    "id": "next",
                    "name": "Next",
                    "rocket": "r1",
                    "links": {},
                },
            ),
            patch(
                "app.services.dashboard_service.ai_service.generate_ai_insights",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            from app.services.dashboard_service import get_dashboard

            result = await get_dashboard()
            assert result.total_launches == 1
            assert result.successful_launches == 1
            assert result.total_starlink == 5000
            assert result.latest_launch is not None
            assert result.next_launch is not None
