"""Tests for the emissions service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.emissions_service import (
    _calc_co2_tonnes,
    _calc_fuel_tonnes,
    _classify_fuel,
    _get_leo_capacity,
)


class TestClassifyFuel:
    def test_rp1_default(self):
        rocket = {"engines": {"propellant_2": "RP-1 kerosene"}}
        assert _classify_fuel(rocket) == "rp1"

    def test_methane(self):
        rocket = {"engines": {"propellant_2": "liquid methane"}}
        assert _classify_fuel(rocket) == "liquid_methane"

    def test_missing_engines(self):
        assert _classify_fuel({}) == "rp1"

    def test_case_insensitive(self):
        rocket = {"engines": {"propellant_2": "LIQUID METHANE"}}
        assert _classify_fuel(rocket) == "liquid_methane"


class TestCalcFuelTonnes:
    def test_single_core(self):
        rocket = {
            "first_stage": {"fuel_amount_tons": 385},
            "second_stage": {"fuel_amount_tons": 90},
            "boosters": 0,
        }
        assert _calc_fuel_tonnes(rocket) == 475.0

    def test_falcon_heavy_with_boosters(self):
        rocket = {
            "first_stage": {"fuel_amount_tons": 385},
            "second_stage": {"fuel_amount_tons": 90},
            "boosters": 2,
        }
        # 385 * 3 + 90 = 1245
        assert _calc_fuel_tonnes(rocket) == 1245.0

    def test_missing_stages(self):
        assert _calc_fuel_tonnes({}) == 0.0


class TestCalcCo2Tonnes:
    def test_rp1(self):
        result = _calc_co2_tonnes(475.0, "rp1")
        # 475 * 1000 * 0.306 * 3.15 / 1000
        assert abs(result - 457.85) < 0.1

    def test_methane(self):
        result = _calc_co2_tonnes(100.0, "liquid_methane")
        # 100 * 1000 * 0.217 * 2.75 / 1000
        assert abs(result - 59.68) < 0.1

    def test_zero_fuel(self):
        assert _calc_co2_tonnes(0, "rp1") == 0.0


class TestGetLeoCapacity:
    def test_finds_leo(self):
        rocket = {
            "payload_weights": [
                {"id": "leo", "name": "Low Earth Orbit", "kg": 22800},
                {"id": "gto", "name": "GTO", "kg": 8300},
            ]
        }
        assert _get_leo_capacity(rocket) == 22800

    def test_matches_by_name(self):
        rocket = {
            "payload_weights": [
                {"id": "x", "name": "low earth orbit", "kg": 10000},
            ]
        }
        assert _get_leo_capacity(rocket) == 10000

    def test_no_leo(self):
        rocket = {"payload_weights": [{"id": "gto", "name": "GTO", "kg": 5000}]}
        assert _get_leo_capacity(rocket) is None

    def test_no_payload_weights(self):
        assert _get_leo_capacity({}) is None


class TestGetEmissionsData:
    @pytest.mark.asyncio
    async def test_full_response(self):
        rockets = [
            {
                "id": "r1",
                "name": "Falcon 9",
                "engines": {"propellant_2": "RP-1"},
                "first_stage": {"fuel_amount_tons": 385},
                "second_stage": {"fuel_amount_tons": 90},
                "boosters": 0,
                "payload_weights": [{"id": "leo", "name": "Low Earth Orbit", "kg": 22800}],
            }
        ]
        launches = [
            {
                "rocket": "r1",
                "date_utc": "2023-01-15T00:00:00Z",
                "upcoming": False,
                "cores": [{"reused": True}],
            },
            {
                "rocket": "r1",
                "date_utc": "2023-06-15T00:00:00Z",
                "upcoming": False,
                "cores": [{"reused": False}],
            },
        ]

        mock_cache = AsyncMock()
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()

        with (
            patch(
                "app.services.emissions_service.get_all_launches",
                new_callable=AsyncMock,
                return_value=launches,
            ),
            patch(
                "app.services.emissions_service.spacex_client.get_rockets",
                new_callable=AsyncMock,
                return_value=rockets,
            ),
            patch("app.services.emissions_service.cache", mock_cache),
        ):
            from app.services.emissions_service import get_emissions_data

            result = await get_emissions_data()
            assert result.total_launches == 2
            assert result.total_reuses == 1
            assert len(result.emissions_by_vehicle) == 1
            assert len(result.annual_emissions) == 1
            assert result.annual_emissions[0].year == 2023
            assert result.reuse_co2_saved_tonnes == 60.0

    @pytest.mark.asyncio
    async def test_returns_cached(self):
        cached_data = {
            "total_co2_tonnes": 100,
            "total_fuel_tonnes": 200,
            "co2_per_launch": 50,
            "reuse_co2_saved_tonnes": 60,
            "total_reuses": 1,
            "total_launches": 2,
            "emissions_by_vehicle": [],
            "annual_emissions": [],
            "fuel_breakdown": [],
        }
        mock_cache = AsyncMock()
        mock_cache.get = AsyncMock(return_value=cached_data)

        with patch("app.services.emissions_service.cache", mock_cache):
            from app.services.emissions_service import get_emissions_data

            result = await get_emissions_data()
            assert result.total_co2_tonnes == 100
