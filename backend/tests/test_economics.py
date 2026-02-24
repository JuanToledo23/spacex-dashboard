"""Tests for the economics service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.economics_service import (
    _build_annual_spend,
    _build_cost_by_vehicle,
    _build_customers,
    _build_orbit_mass,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ROCKETS = [
    {
        "id": "r1",
        "name": "Falcon 9",
        "cost_per_launch": 50_000_000,
        "payload_weights": [{"name": "Low Earth Orbit", "id": "leo", "kg": 22_800}],
    },
    {
        "id": "r2",
        "name": "Falcon Heavy",
        "cost_per_launch": 90_000_000,
        "payload_weights": [{"name": "Low Earth Orbit", "id": "leo", "kg": 63_800}],
    },
]

LAUNCHES = [
    {"id": "l1", "date_utc": "2023-01-15T00:00:00Z", "rocket": "r1", "upcoming": False},
    {"id": "l2", "date_utc": "2023-06-20T00:00:00Z", "rocket": "r1", "upcoming": False},
    {"id": "l3", "date_utc": "2024-03-01T00:00:00Z", "rocket": "r2", "upcoming": False},
    {"id": "l4", "date_utc": "2025-01-01T00:00:00Z", "rocket": "r1", "upcoming": True},
]

PAYLOADS = [
    {"id": "p1", "customers": ["NASA"], "mass_kg": 5000, "orbit": "LEO"},
    {"id": "p2", "customers": ["NASA", "SpaceX"], "mass_kg": 2000, "orbit": "GTO"},
    {"id": "p3", "customers": ["SpaceX"], "mass_kg": None, "orbit": "LEO"},
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestBuildCostByVehicle:
    def test_calculates_total_spend(self):
        counts = {"r1": 2, "r2": 1}
        result = _build_cost_by_vehicle(ROCKETS, counts)

        f9 = next(v for v in result if v.rocket_name == "Falcon 9")
        assert f9.total_spend == 100_000_000
        assert f9.launches == 2

        fh = next(v for v in result if v.rocket_name == "Falcon Heavy")
        assert fh.total_spend == 90_000_000
        assert fh.launches == 1

    def test_cost_per_kg_calculated(self):
        counts = {"r1": 1}
        result = _build_cost_by_vehicle(ROCKETS, counts)

        f9 = next(v for v in result if v.rocket_name == "Falcon 9")
        assert f9.cost_per_kg_leo == pytest.approx(50_000_000 / 22_800, rel=0.01)

    def test_sorted_by_total_spend_descending(self):
        counts = {"r1": 2, "r2": 1}
        result = _build_cost_by_vehicle(ROCKETS, counts)
        assert result[0].total_spend >= result[1].total_spend

    def test_zero_launches_returns_zero_spend(self):
        result = _build_cost_by_vehicle(ROCKETS, {})
        for v in result:
            assert v.total_spend == 0
            assert v.launches == 0


class TestBuildAnnualSpend:
    def test_groups_by_year(self):
        rocket_cost_map = {"r1": 50_000_000, "r2": 90_000_000}
        result = _build_annual_spend(LAUNCHES, rocket_cost_map)

        years = [a.year for a in result]
        assert 2023 in years
        assert 2024 in years

    def test_excludes_upcoming(self):
        rocket_cost_map = {"r1": 50_000_000}
        result = _build_annual_spend(LAUNCHES, rocket_cost_map)

        years = [a.year for a in result]
        assert 2025 not in years

    def test_avg_cost_calculated(self):
        rocket_cost_map = {"r1": 50_000_000, "r2": 90_000_000}
        result = _build_annual_spend(LAUNCHES, rocket_cost_map)

        y2023 = next(a for a in result if a.year == 2023)
        assert y2023.launches == 2
        assert y2023.avg_cost == 50_000_000


class TestBuildCustomers:
    def test_aggregates_customers(self):
        result = _build_customers(PAYLOADS)

        nasa = next(c for c in result if c.customer == "NASA")
        assert nasa.payloads == 2
        assert nasa.total_mass_kg == 7000.0

    def test_limits_to_15(self):
        many = [
            {"id": f"p{i}", "customers": [f"C{i}"], "mass_kg": 100, "orbit": "LEO"}
            for i in range(20)
        ]
        result = _build_customers(many)
        assert len(result) <= 15


class TestBuildOrbitMass:
    def test_groups_by_orbit(self):
        result = _build_orbit_mass(PAYLOADS)

        leo = next(o for o in result if o.orbit == "LEO")
        assert leo.payloads == 2
        assert leo.total_mass_kg == 5000.0  # None mass treated as 0

    def test_excludes_zero_mass_orbits(self):
        data = [{"orbit": "SSO", "mass_kg": 0, "customers": []}]
        result = _build_orbit_mass(data)
        assert len(result) == 0


class TestGetEconomicsData:
    @pytest.mark.asyncio
    async def test_full_economics_response(self):
        mock_cache = AsyncMock()
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()

        with (
            patch("app.services.economics_service.cache", mock_cache),
            patch(
                "app.services.economics_service.get_all_launches",
                new_callable=AsyncMock,
                return_value=LAUNCHES,
            ),
            patch(
                "app.services.economics_service.spacex_client.get_rockets",
                new_callable=AsyncMock,
                return_value=ROCKETS,
            ),
            patch(
                "app.services.economics_service._get_all_payloads",
                new_callable=AsyncMock,
                return_value=PAYLOADS,
            ),
        ):
            from app.services.economics_service import get_economics_data

            result = await get_economics_data()
            assert result.total_launches == 3
            assert result.total_payloads == 3
            assert len(result.cost_by_vehicle) == 2
            assert len(result.annual_spend) >= 1
            assert result.lowest_cost_vehicle in ("Falcon 9", "Falcon Heavy")
            mock_cache.set.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_cached(self):
        cached_data = {
            "total_estimated_spend": 1000,
            "total_launches": 5,
            "total_payloads": 10,
            "total_mass_launched_kg": 50000,
            "avg_cost_per_launch": 200,
            "lowest_cost_per_kg": 2700,
            "lowest_cost_vehicle": "Falcon 9",
            "cost_by_vehicle": [],
            "annual_spend": [],
            "top_customers": [],
            "mass_by_orbit": [],
        }
        mock_cache = AsyncMock()
        mock_cache.get = AsyncMock(return_value=cached_data)

        with patch("app.services.economics_service.cache", mock_cache):
            from app.services.economics_service import get_economics_data

            result = await get_economics_data()
            assert result.total_estimated_spend == 1000
