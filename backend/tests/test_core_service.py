"""Tests for the core/fleet service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.core_service import _parse_core, get_fleet_stats

SAMPLE_CORE = {
    "id": "core1",
    "serial": "B1051",
    "status": "active",
    "reuse_count": 10,
    "rtls_landings": 3,
    "rtls_attempts": 4,
    "asds_landings": 6,
    "asds_attempts": 7,
    "launches": ["l1", "l2", "l3"],
}


class TestParseCore:
    def test_parses_all_fields(self):
        result = _parse_core(SAMPLE_CORE)
        assert result.serial == "B1051"
        assert result.status == "active"
        assert result.reuse_count == 10
        assert result.rtls_landings == 3
        assert result.asds_landings == 6
        assert result.total_landings == 9
        assert result.total_attempts == 11
        assert result.launches == 3

    def test_handles_none_values(self):
        raw = {
            "id": "c2",
            "rtls_landings": None,
            "asds_landings": None,
            "rtls_attempts": None,
            "asds_attempts": None,
            "reuse_count": None,
        }
        result = _parse_core(raw)
        assert result.total_landings == 0
        assert result.total_attempts == 0
        assert result.reuse_count == 0

    def test_empty_launches(self):
        raw = {"id": "c3"}
        result = _parse_core(raw)
        assert result.launches == 0


class TestGetFleetStats:
    @pytest.mark.asyncio
    async def test_fleet_stats_aggregation(self):
        cores = [
            {
                "id": "c1",
                "serial": "B1",
                "status": "active",
                "reuse_count": 10,
                "rtls_landings": 2,
                "rtls_attempts": 3,
                "asds_landings": 4,
                "asds_attempts": 5,
                "launches": ["l1"],
            },
            {
                "id": "c2",
                "serial": "B2",
                "status": "retired",
                "reuse_count": 3,
                "rtls_landings": 1,
                "rtls_attempts": 1,
                "asds_landings": 2,
                "asds_attempts": 3,
                "launches": ["l2", "l3"],
            },
            {
                "id": "c3",
                "serial": "B3",
                "status": "lost",
                "reuse_count": 0,
                "rtls_landings": 0,
                "rtls_attempts": 0,
                "asds_landings": 0,
                "asds_attempts": 1,
                "launches": [],
            },
        ]
        with patch(
            "app.services.core_service.get_all_cores",
            new_callable=AsyncMock,
            return_value=cores,
        ):
            stats = await get_fleet_stats()
            assert stats.total_cores == 3
            assert stats.active_cores == 1
            assert stats.retired_cores == 1
            assert stats.lost_cores == 1
            assert stats.total_landings == 9
            assert stats.total_landing_attempts == 13
            assert stats.rtls_landings == 3
            assert stats.asds_landings == 6
            assert len(stats.most_reused) == 3

    @pytest.mark.asyncio
    async def test_most_reused_sorted(self):
        cores = [
            {
                "id": f"c{i}",
                "serial": f"B{i}",
                "status": "active",
                "reuse_count": i,
                "rtls_landings": 0,
                "rtls_attempts": 0,
                "asds_landings": 0,
                "asds_attempts": 0,
                "launches": [],
            }
            for i in range(15)
        ]
        with patch(
            "app.services.core_service.get_all_cores",
            new_callable=AsyncMock,
            return_value=cores,
        ):
            stats = await get_fleet_stats()
            assert len(stats.most_reused) == 10
            assert stats.most_reused[0].reuse_count == 14
