"""Tests for the rocket detail service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.rocket_detail_service import _parse_engine, _parse_stage, get_rocket_detail


class TestParseEngine:
    def test_parses_full_engine(self):
        raw = {
            "number": 9,
            "type": "merlin",
            "version": "1D+",
            "propellant_1": "liquid oxygen",
            "propellant_2": "RP-1 kerosene",
            "thrust_sea_level": {"kN": 845},
            "thrust_vacuum": {"kN": 981},
            "isp": {"sea_level": 282, "vacuum": 311},
            "thrust_to_weight": 180.1,
        }
        result = _parse_engine(raw)
        assert result.number == 9
        assert result.type == "merlin"
        assert result.thrust_sea_level_kn == 845
        assert result.thrust_vacuum_kn == 981
        assert result.isp_sea_level == 282
        assert result.isp_vacuum == 311

    def test_handles_empty(self):
        result = _parse_engine({})
        assert result.number is None
        assert result.thrust_sea_level_kn is None


class TestParseStage:
    def test_parses_stage(self):
        raw = {
            "reusable": True,
            "engines": 9,
            "fuel_amount_tons": 385.6,
            "burn_time_sec": 162,
            "thrust_sea_level": {"kN": 7607},
            "thrust_vacuum": {"kN": 8227},
        }
        result = _parse_stage(raw)
        assert result.reusable is True
        assert result.engines == 9
        assert result.fuel_amount_tons == 385.6
        assert result.thrust_sea_level_kn == 7607

    def test_handles_empty(self):
        result = _parse_stage({})
        assert result.reusable is None
        assert result.engines is None


class TestGetRocketDetail:
    @pytest.mark.asyncio
    async def test_builds_full_detail(self):
        rocket_raw = {
            "id": "r1",
            "name": "Falcon 9",
            "type": "rocket",
            "active": True,
            "stages": 2,
            "boosters": 0,
            "cost_per_launch": 50000000,
            "first_flight": "2010-06-04",
            "country": "United States",
            "description": "Two-stage rocket",
            "wikipedia": "https://wiki.org",
            "flickr_images": ["img1.jpg"],
            "height": {"meters": 70},
            "diameter": {"meters": 3.7},
            "mass": {"kg": 549054},
            "engines": {
                "number": 9,
                "type": "merlin",
                "version": "1D+",
                "propellant_1": "LOX",
                "propellant_2": "RP-1",
                "thrust_sea_level": {"kN": 845},
                "thrust_vacuum": {"kN": 981},
                "isp": {"sea_level": 282, "vacuum": 311},
                "thrust_to_weight": 180,
            },
            "first_stage": {"reusable": True, "engines": 9, "fuel_amount_tons": 385},
            "second_stage": {"reusable": False, "engines": 1, "fuel_amount_tons": 90},
            "landing_legs": {"number": 4, "material": "carbon fiber"},
            "payload_weights": [{"id": "leo", "name": "Low Earth Orbit", "kg": 22800, "lb": 50265}],
        }
        launches = [
            {"rocket": "r1", "success": True},
            {"rocket": "r1", "success": True},
            {"rocket": "r1", "success": False},
            {"rocket": "r2", "success": True},
        ]

        with (
            patch(
                "app.services.rocket_detail_service.spacex_client.get_rocket",
                new_callable=AsyncMock,
                return_value=rocket_raw,
            ),
            patch(
                "app.services.rocket_detail_service.get_all_launches",
                new_callable=AsyncMock,
                return_value=launches,
            ),
        ):
            result = await get_rocket_detail("r1")
            assert result.name == "Falcon 9"
            assert result.launch_count == 3
            assert result.success_rate_pct == 66.7
            assert result.height_meters == 70
            assert result.engines.number == 9
            assert result.first_stage.reusable is True
            assert result.landing_legs_number == 4
            assert len(result.payload_weights) == 1
