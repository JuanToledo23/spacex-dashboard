"""Tests for the Starlink service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.starlink_service import (
    _parse_satellite,
    get_starlink,
    get_starlink_positions,
    get_starlink_stats,
)

SAMPLE_SAT_RAW = {
    "id": "sat1",
    "version": "v1.5",
    "height_km": 550.5,
    "latitude": 45.0,
    "longitude": -93.0,
    "velocity_kms": 7.6,
    "launch": "launch1",
    "spaceTrack": {"OBJECT_NAME": "STARLINK-1234", "APOAPSIS": 551},
}


class TestParseSatellite:
    def test_parses_all_fields(self):
        result = _parse_satellite(SAMPLE_SAT_RAW)
        assert result.id == "sat1"
        assert result.object_name == "STARLINK-1234"
        assert result.version == "v1.5"
        assert result.height_km == 550.5
        assert result.latitude == 45.0
        assert result.longitude == -93.0
        assert result.velocity_kms == 7.6
        assert result.launch_id == "launch1"

    def test_height_from_spacetrack_fallback(self):
        raw = {"id": "s2", "spaceTrack": {"APOAPSIS": 400}}
        result = _parse_satellite(raw)
        assert result.height_km == 400.0

    def test_missing_spacetrack(self):
        raw = {"id": "s3"}
        result = _parse_satellite(raw)
        assert result.object_name is None
        assert result.height_km is None

    def test_none_height(self):
        raw = {"id": "s4", "spaceTrack": {}}
        result = _parse_satellite(raw)
        assert result.height_km is None


class TestGetStarlink:
    @pytest.mark.asyncio
    async def test_pagination(self):
        sats = [{"id": f"s{i}", "version": "v1.5", "spaceTrack": {}} for i in range(5)]
        with patch(
            "app.services.starlink_service.get_all_starlink",
            new_callable=AsyncMock,
            return_value=sats,
        ):
            items, total = await get_starlink(page=1, limit=2)
            assert total == 5
            assert len(items) == 2
            assert items[0].id == "s0"
            assert items[1].id == "s1"

    @pytest.mark.asyncio
    async def test_second_page(self):
        sats = [{"id": f"s{i}", "version": "v1.5", "spaceTrack": {}} for i in range(5)]
        with patch(
            "app.services.starlink_service.get_all_starlink",
            new_callable=AsyncMock,
            return_value=sats,
        ):
            items, total = await get_starlink(page=2, limit=2)
            assert total == 5
            assert len(items) == 2
            assert items[0].id == "s2"

    @pytest.mark.asyncio
    async def test_version_filter(self):
        sats = [
            {"id": "s1", "version": "v1.5", "spaceTrack": {}},
            {"id": "s2", "version": "v2.0", "spaceTrack": {}},
            {"id": "s3", "version": "v1.5", "spaceTrack": {}},
        ]
        with patch(
            "app.services.starlink_service.get_all_starlink",
            new_callable=AsyncMock,
            return_value=sats,
        ):
            items, total = await get_starlink(version="v2.0")
            assert total == 1
            assert items[0].id == "s2"


class TestGetStarlinkPositions:
    @pytest.mark.asyncio
    async def test_filters_out_missing_coords(self):
        sats = [
            {"id": "s1", "latitude": 10, "longitude": 20, "spaceTrack": {}},
            {"id": "s2", "latitude": None, "longitude": 20, "spaceTrack": {}},
            {"id": "s3", "latitude": 30, "longitude": None, "spaceTrack": {}},
        ]
        with patch(
            "app.services.starlink_service.get_all_starlink",
            new_callable=AsyncMock,
            return_value=sats,
        ):
            positions = await get_starlink_positions()
            assert len(positions) == 1
            assert positions[0].id == "s1"

    @pytest.mark.asyncio
    async def test_position_data(self):
        sats = [
            {
                "id": "s1",
                "latitude": 45.5,
                "longitude": -93.2,
                "height_km": 550,
                "velocity_kms": 7.6,
                "version": "v2.0",
                "spaceTrack": {"OBJECT_NAME": "STARLINK-5000"},
            },
        ]
        with patch(
            "app.services.starlink_service.get_all_starlink",
            new_callable=AsyncMock,
            return_value=sats,
        ):
            positions = await get_starlink_positions()
            assert positions[0].latitude == 45.5
            assert positions[0].object_name == "STARLINK-5000"
            assert positions[0].height_km == 550.0


class TestGetStarlinkStats:
    @pytest.mark.asyncio
    async def test_stats_aggregation(self):
        sats = [
            {"id": "s1", "version": "v1.5", "height_km": 500, "spaceTrack": {}},
            {"id": "s2", "version": "v2.0", "height_km": 600, "spaceTrack": {}},
            {"id": "s3", "version": "v1.5", "spaceTrack": {"APOAPSIS": 400}},
        ]
        with patch(
            "app.services.starlink_service.get_all_starlink",
            new_callable=AsyncMock,
            return_value=sats,
        ):
            stats = await get_starlink_stats()
            assert stats["total"] == 3
            assert len(stats["by_version"]) == 2
            assert stats["avg_height_km"] == 500.0

    @pytest.mark.asyncio
    async def test_empty_sats(self):
        with patch(
            "app.services.starlink_service.get_all_starlink",
            new_callable=AsyncMock,
            return_value=[],
        ):
            stats = await get_starlink_stats()
            assert stats["total"] == 0
            assert stats["avg_height_km"] == 0
