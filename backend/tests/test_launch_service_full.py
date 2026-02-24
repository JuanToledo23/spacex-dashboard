"""Tests for the launch service: filters, sorting, and edge cases."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.launch_service import _parse_launch, get_launches, get_launches_by_year

SAMPLE_LAUNCHES = [
    {
        "id": "l1",
        "name": "FalconSat",
        "date_utc": "2006-03-24T22:30:00.000Z",
        "success": False,
        "upcoming": False,
        "rocket": "r1",
        "links": {"patch": {"small": "p1.png"}},
    },
    {
        "id": "l2",
        "name": "Starlink 4-1",
        "date_utc": "2022-01-06T21:49:00.000Z",
        "success": True,
        "upcoming": False,
        "rocket": "r2",
        "links": {"patch": {"small": "p2.png"}},
    },
    {
        "id": "l3",
        "name": "Crew-5",
        "date_utc": "2022-10-05T16:00:00.000Z",
        "success": True,
        "upcoming": False,
        "rocket": "r2",
        "links": {},
    },
    {
        "id": "l4",
        "name": "Starship IFT-3",
        "date_utc": "2024-03-14T13:25:00.000Z",
        "success": None,
        "upcoming": True,
        "rocket": "r3",
        "links": {},
    },
]


class TestParseLaunch:
    def test_full_parse(self):
        result = _parse_launch(SAMPLE_LAUNCHES[0], {"r1": "Falcon 1"})
        assert result.id == "l1"
        assert result.name == "FalconSat"
        assert result.rocket_name == "Falcon 1"
        assert result.patch_small == "p1.png"

    def test_no_rocket_map(self):
        result = _parse_launch(SAMPLE_LAUNCHES[0])
        assert result.rocket_name is None

    def test_missing_links(self):
        raw = {"id": "x", "name": "Test"}
        result = _parse_launch(raw)
        assert result.patch_small is None


class TestGetLaunches:
    @pytest.fixture(autouse=True)
    def _mock_data(self):
        with (
            patch(
                "app.services.launch_service.get_all_launches",
                new_callable=AsyncMock,
                return_value=list(SAMPLE_LAUNCHES),
            ),
            patch(
                "app.services.launch_service.cache.get",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            yield

    @pytest.mark.asyncio
    async def test_default_pagination(self):
        items, total = await get_launches()
        assert total == 4

    @pytest.mark.asyncio
    async def test_filter_success_true(self):
        items, total = await get_launches(success=True)
        assert total == 2
        assert all(i.success for i in items)

    @pytest.mark.asyncio
    async def test_filter_success_false(self):
        items, total = await get_launches(success=False)
        assert total == 1
        assert items[0].name == "FalconSat"

    @pytest.mark.asyncio
    async def test_filter_upcoming(self):
        items, total = await get_launches(upcoming=True)
        assert total == 1
        assert items[0].name == "Starship IFT-3"

    @pytest.mark.asyncio
    async def test_filter_rocket_id(self):
        items, total = await get_launches(rocket_id="r2")
        assert total == 2

    @pytest.mark.asyncio
    async def test_filter_date_range(self):
        items, total = await get_launches(from_date="2022-01-01", to_date="2022-12-31")
        assert total == 2

    @pytest.mark.asyncio
    async def test_sort_asc(self):
        items, _ = await get_launches(sort="date_utc", order="asc")
        dates = [i.date_utc for i in items]
        assert dates == sorted(dates)

    @pytest.mark.asyncio
    async def test_sort_by_name(self):
        items, _ = await get_launches(sort="name", order="asc")
        names = [i.name for i in items]
        assert names == sorted(names)

    @pytest.mark.asyncio
    async def test_pagination_limit(self):
        items, total = await get_launches(page=1, limit=2)
        assert len(items) == 2
        assert total == 4

    @pytest.mark.asyncio
    async def test_pagination_page_2(self):
        items, total = await get_launches(page=2, limit=2)
        assert len(items) == 2


class TestGetLaunchesByYear:
    @pytest.mark.asyncio
    async def test_aggregation(self):
        with patch(
            "app.services.launch_service.get_all_launches",
            new_callable=AsyncMock,
            return_value=SAMPLE_LAUNCHES,
        ):
            result = await get_launches_by_year()
            years = {r.year: r for r in result}
            assert 2006 in years
            assert years[2006].total == 1
            assert years[2006].failures == 1
            assert 2022 in years
            assert years[2022].successes == 2

    @pytest.mark.asyncio
    async def test_skips_upcoming(self):
        with patch(
            "app.services.launch_service.get_all_launches",
            new_callable=AsyncMock,
            return_value=SAMPLE_LAUNCHES,
        ):
            result = await get_launches_by_year()
            years = [r.year for r in result]
            # 2024 launch is upcoming - should not be counted
            assert 2024 not in years
