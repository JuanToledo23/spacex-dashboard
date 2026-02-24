"""Tests for the roadster service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.roadster_service import _fetch_roadster

SAMPLE_RAW = {
    "name": "Elon Musk's Tesla Roadster",
    "launch_date_utc": "2018-02-06T20:45:00.000Z",
    "speed_kph": 9521,
    "earth_distance_km": 320600000,
    "earth_distance_mi": 199200000,
    "mars_distance_km": 150000000,
    "mars_distance_mi": 93000000,
    "orbit_type": "heliocentric",
    "period_days": 557.2,
    "apoapsis_au": 1.664,
    "periapsis_au": 0.986,
    "semi_major_axis_au": 1.325,
    "eccentricity": 0.256,
    "inclination": 1.078,
    "details": "Starman in a Tesla",
    "wikipedia": "https://en.wikipedia.org/wiki/Elon_Musk%27s_Tesla_Roadster",
    "video": "https://youtu.be/wbSwFU6tY1c",
    "flickr_images": ["img1.jpg", "img2.jpg"],
}


class TestFetchRoadster:
    @pytest.mark.asyncio
    async def test_parses_all_fields(self):
        with patch(
            "app.services.roadster_service.spacex_client.get_roadster",
            new_callable=AsyncMock,
            return_value=SAMPLE_RAW,
        ):
            result = await _fetch_roadster()
            assert result["name"] == "Elon Musk's Tesla Roadster"
            assert result["speed_kph"] == 9521
            assert result["orbit_type"] == "heliocentric"
            assert result["period_days"] == 557.2
            assert result["apoapsis_au"] == 1.664
            assert result["periapsis_au"] == 0.986
            assert len(result["flickr_images"]) == 2
            assert result["semi_major_axis_au"] == 1.325

    @pytest.mark.asyncio
    async def test_handles_missing_optional_fields(self):
        raw = {
            "name": "Roadster",
            "launch_date_utc": "2018-02-06",
        }
        with patch(
            "app.services.roadster_service.spacex_client.get_roadster",
            new_callable=AsyncMock,
            return_value=raw,
        ):
            result = await _fetch_roadster()
            assert result["name"] == "Roadster"
            assert result["speed_kph"] == 0
            assert result["flickr_images"] == []
            assert result["semi_major_axis_au"] is None
