"""Tests for the landing/landpad service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.landing_service import _fetch_landing

SAMPLE_RAW = [
    {
        "id": "lp1",
        "name": "LZ-1",
        "full_name": "Landing Zone 1",
        "type": "RTLS",
        "status": "active",
        "locality": "Cape Canaveral",
        "region": "Florida",
        "latitude": 28.485,
        "longitude": -80.544,
        "landing_attempts": 20,
        "landing_successes": 18,
    },
    {
        "id": "lp2",
        "name": "OCISLY",
        "full_name": "Of Course I Still Love You",
        "type": "ASDS",
        "status": "active",
        "locality": "Port Canaveral",
        "region": "Florida",
        "latitude": 28.405,
        "longitude": -80.596,
        "landing_attempts": 50,
        "landing_successes": 45,
    },
]


class TestFetchLanding:
    @pytest.mark.asyncio
    async def test_parses_landpads(self):
        with patch(
            "app.services.landing_service.spacex_client.get_landpads",
            new_callable=AsyncMock,
            return_value=SAMPLE_RAW,
        ):
            result = await _fetch_landing()
            assert len(result["landpads"]) == 2
            # Sorted by attempts descending
            assert result["landpads"][0]["name"] == "OCISLY"

    @pytest.mark.asyncio
    async def test_stats_aggregation(self):
        with patch(
            "app.services.landing_service.spacex_client.get_landpads",
            new_callable=AsyncMock,
            return_value=SAMPLE_RAW,
        ):
            result = await _fetch_landing()
            stats = result["stats"]
            assert stats["total_attempts"] == 70
            assert stats["total_successes"] == 63
            assert stats["rtls_attempts"] == 20
            assert stats["rtls_successes"] == 18
            assert stats["asds_attempts"] == 50
            assert stats["asds_successes"] == 45

    @pytest.mark.asyncio
    async def test_success_rate_calculation(self):
        with patch(
            "app.services.landing_service.spacex_client.get_landpads",
            new_callable=AsyncMock,
            return_value=SAMPLE_RAW,
        ):
            result = await _fetch_landing()
            stats = result["stats"]
            assert stats["overall_success_rate"] == 90.0

    @pytest.mark.asyncio
    async def test_empty_landpads(self):
        with patch(
            "app.services.landing_service.spacex_client.get_landpads",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await _fetch_landing()
            assert result["stats"]["total_attempts"] == 0
            assert result["stats"]["overall_success_rate"] == 0.0
