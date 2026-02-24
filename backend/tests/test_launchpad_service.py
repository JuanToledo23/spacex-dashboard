"""Tests for the launchpad service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.launchpad_service import _fetch_launchpads

SAMPLE_RAW = [
    {
        "id": "lp1",
        "name": "VAFB SLC 4E",
        "full_name": "Vandenberg SLC-4E",
        "locality": "Vandenberg",
        "region": "California",
        "latitude": 34.632,
        "longitude": -120.611,
        "launch_attempts": 15,
        "launch_successes": 14,
        "status": "active",
    },
    {
        "id": "lp2",
        "name": "KSC LC 39A",
        "full_name": "Kennedy Space Center LC-39A",
        "locality": "Cape Canaveral",
        "region": "Florida",
        "latitude": 28.608,
        "longitude": -80.604,
        "launch_attempts": 50,
        "launch_successes": 49,
        "status": "active",
    },
]


class TestFetchLaunchpads:
    @pytest.mark.asyncio
    async def test_parses_all_pads(self):
        with patch(
            "app.services.launchpad_service.spacex_client.get_launchpads",
            new_callable=AsyncMock,
            return_value=SAMPLE_RAW,
        ):
            result = await _fetch_launchpads()
            assert len(result) == 2
            assert result[0]["name"] == "VAFB SLC 4E"
            assert result[1]["launch_attempts"] == 50

    @pytest.mark.asyncio
    async def test_handles_missing_fields(self):
        raw = [{"id": "lp3"}]
        with patch(
            "app.services.launchpad_service.spacex_client.get_launchpads",
            new_callable=AsyncMock,
            return_value=raw,
        ):
            result = await _fetch_launchpads()
            assert len(result) == 1
            assert result[0]["name"] == ""
            assert result[0]["status"] == "unknown"
