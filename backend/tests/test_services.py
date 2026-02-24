from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_get_rockets_enriches_with_launch_data(mock_cache, sample_rockets, sample_launches):
    with patch("app.services.rocket_service.spacex_client") as mock_client:
        mock_client.get_rockets = AsyncMock(return_value=sample_rockets)
        mock_client.get_launches = AsyncMock(return_value=sample_launches)

        from app.services.rocket_service import get_rockets

        rockets = await get_rockets()

        assert len(rockets) == 2

        falcon1 = next(r for r in rockets if r.name == "Falcon 1")
        assert falcon1.launch_count == 1
        assert falcon1.success_rate_pct == 0.0

        falcon9 = next(r for r in rockets if r.name == "Falcon 9")
        assert falcon9.launch_count == 1
        assert falcon9.success_rate_pct == 100.0


@pytest.mark.asyncio
async def test_launches_by_year_aggregation(mock_cache, sample_launches):
    with patch(
        "app.services.launch_service.get_all_launches",
        new_callable=AsyncMock,
        return_value=sample_launches,
    ):
        from app.services.launch_service import get_launches_by_year

        aggregates = await get_launches_by_year()

        assert len(aggregates) == 2
        year_2006 = next(a for a in aggregates if a.year == 2006)
        assert year_2006.failures == 1
        assert year_2006.successes == 0

        year_2023 = next(a for a in aggregates if a.year == 2023)
        assert year_2023.successes == 1
        assert year_2023.failures == 0


@pytest.mark.asyncio
async def test_launches_pagination(mock_cache, sample_launches):
    with (
        patch(
            "app.services.launch_service.get_all_launches",
            new_callable=AsyncMock,
            return_value=sample_launches,
        ),
        patch(
            "app.services.launch_service.cache",
        ) as cache_mock,
    ):
        cache_mock.get = AsyncMock(return_value=None)

        from app.services.launch_service import get_launches

        items, total = await get_launches(page=1, limit=1)
        assert total == 2
        assert len(items) == 1
