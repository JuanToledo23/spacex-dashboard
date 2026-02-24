"""Tests for the launch detail service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.launch_detail_service import (
    _parse_cores,
    _parse_crew,
    _parse_links,
    _parse_payloads,
    get_launch_detail,
)


class TestParseCores:
    def test_parses_core_list(self):
        raw = [
            {
                "core": "B1051",
                "flight": 10,
                "reused": True,
                "landing_attempt": True,
                "landing_success": True,
                "landing_type": "ASDS",
            }
        ]
        result = _parse_cores(raw)
        assert len(result) == 1
        assert result[0].serial == "B1051"
        assert result[0].flight == 10
        assert result[0].reused is True
        assert result[0].landing_type == "ASDS"

    def test_empty_list(self):
        assert _parse_cores([]) == []


class TestParseLinks:
    def test_parses_all_link_fields(self):
        raw = {
            "webcast": "https://youtube.com/watch?v=abc",
            "article": "https://example.com",
            "wikipedia": "https://wiki.org",
            "presskit": "https://press.pdf",
            "reddit": {"campaign": "https://reddit.com/r/spacex"},
            "flickr": {"original": ["img1.jpg", "img2.jpg"]},
            "patch": {"small": "s.png", "large": "l.png"},
        }
        result = _parse_links(raw)
        assert result.webcast == "https://youtube.com/watch?v=abc"
        assert result.reddit_campaign == "https://reddit.com/r/spacex"
        assert len(result.flickr_original) == 2
        assert result.patch_small == "s.png"

    def test_handles_missing_nested(self):
        raw = {}
        result = _parse_links(raw)
        assert result.webcast is None
        assert result.flickr_original == []
        assert result.patch_small is None


class TestParsePayloads:
    def test_parses_payload_list(self):
        raw = [
            {
                "id": "p1",
                "name": "Starlink Group 6-1",
                "type": "Satellite",
                "customers": ["SpaceX"],
                "mass_kg": 17400,
                "orbit": "LEO",
                "regime": "low-earth",
            }
        ]
        result = _parse_payloads(raw)
        assert len(result) == 1
        assert result[0].name == "Starlink Group 6-1"
        assert result[0].mass_kg == 17400


class TestParseCrew:
    def test_parses_with_roles(self):
        raw = [{"id": "c1", "name": "Bob", "agency": "NASA", "image": "bob.jpg"}]
        role_map = {"c1": "Commander"}
        result = _parse_crew(raw, role_map)
        assert result[0].name == "Bob"
        assert result[0].role == "Commander"

    def test_missing_role(self):
        raw = [{"id": "c2", "name": "Alice"}]
        result = _parse_crew(raw, {})
        assert result[0].role is None


class TestGetLaunchDetail:
    @pytest.mark.asyncio
    async def test_full_detail_fetch(self):
        launch_raw = {
            "id": "launch1",
            "flight_number": 100,
            "name": "CRS-25",
            "date_utc": "2023-07-14T00:00:00.000Z",
            "success": True,
            "upcoming": False,
            "details": "Supply mission",
            "rocket": "r1",
            "launchpad": "lp1",
            "cores": [{"core": "core1", "flight": 5, "reused": True}],
            "crew": [{"crew": "c1", "role": "Commander"}],
            "payloads": ["p1"],
            "failures": [],
            "fairings": {"recovered": True, "reused": False},
            "links": {
                "webcast": "https://yt.com",
                "patch": {"small": "s.png"},
                "reddit": {},
                "flickr": {},
            },
            "static_fire_date_utc": "2023-07-10",
        }

        with (
            patch(
                "app.services.launch_detail_service.spacex_client.get_launch",
                new_callable=AsyncMock,
                return_value=launch_raw,
            ),
            patch(
                "app.services.launch_detail_service.spacex_client.get_payloads_by_ids",
                new_callable=AsyncMock,
                return_value=[{"id": "p1", "name": "Dragon CRS-25"}],
            ),
            patch(
                "app.services.launch_detail_service.spacex_client.get_crew_by_ids",
                new_callable=AsyncMock,
                return_value=[{"id": "c1", "name": "Bob"}],
            ),
            patch(
                "app.services.launch_detail_service.cache.get",
                new_callable=AsyncMock,
                return_value=[
                    {"id": "r1", "name": "Falcon 9"},
                ],
            ),
        ):
            result = await get_launch_detail("launch1")
            assert result.name == "CRS-25"
            assert result.rocket_name == "Falcon 9"
            assert result.fairings_recovered is True
            assert len(result.crew) == 1

    @pytest.mark.asyncio
    async def test_crew_string_format(self):
        """v5 crew can be plain string IDs."""
        launch_raw = {
            "id": "l2",
            "rocket": "r1",
            "launchpad": "lp1",
            "cores": [],
            "crew": ["c1_str"],
            "payloads": [],
            "failures": [],
            "links": {},
        }

        with (
            patch(
                "app.services.launch_detail_service.spacex_client.get_launch",
                new_callable=AsyncMock,
                return_value=launch_raw,
            ),
            patch(
                "app.services.launch_detail_service.spacex_client.get_payloads_by_ids",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "app.services.launch_detail_service.spacex_client.get_crew_by_ids",
                new_callable=AsyncMock,
                return_value=[{"id": "c1_str", "name": "Astronaut"}],
            ),
            patch(
                "app.services.launch_detail_service.cache.get",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            result = await get_launch_detail("l2")
            assert len(result.crew) == 1
            assert result.crew[0].name == "Astronaut"
