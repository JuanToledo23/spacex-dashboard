"""Tests for the history service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.history_service import _fetch_history

SAMPLE_RAW = [
    {
        "id": "h2",
        "title": "Falcon 9 Reuse",
        "event_date_utc": "2017-03-30T00:00:00.000Z",
        "details": "First reflight",
        "links": {
            "article": "https://example.com/reflight",
            "wikipedia": "https://en.wikipedia.org/wiki/Reflight",
        },
    },
    {
        "id": "h1",
        "title": "Falcon 1 Success",
        "event_date_utc": "2008-09-28T00:00:00.000Z",
        "details": "Fourth flight",
        "links": {"article": "https://example.com/f1"},
    },
]


class TestFetchHistory:
    @pytest.mark.asyncio
    async def test_parses_and_sorts_events(self):
        with patch(
            "app.services.history_service.spacex_client.get_history",
            new_callable=AsyncMock,
            return_value=SAMPLE_RAW,
        ):
            result = await _fetch_history()
            events = result["events"]
            assert len(events) == 2
            assert result["total"] == 2
            # Events should be sorted by date ascending
            assert events[0]["title"] == "Falcon 1 Success"
            assert events[1]["title"] == "Falcon 9 Reuse"

    @pytest.mark.asyncio
    async def test_handles_missing_links(self):
        raw = [
            {
                "id": "h3",
                "title": "Test Event",
                "event_date_utc": "2020-01-01T00:00:00.000Z",
            }
        ]
        with patch(
            "app.services.history_service.spacex_client.get_history",
            new_callable=AsyncMock,
            return_value=raw,
        ):
            result = await _fetch_history()
            assert result["events"][0]["article"] is None
            assert result["events"][0]["wikipedia"] is None

    @pytest.mark.asyncio
    async def test_empty_history(self):
        with patch(
            "app.services.history_service.spacex_client.get_history",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await _fetch_history()
            assert result["total"] == 0
            assert result["events"] == []
