"""Tests for the SpaceX API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.clients.spacex_client import SpaceXAPIError, SpaceXClient


class TestSpaceXAPIError:
    def test_stores_status_code_and_message(self):
        err = SpaceXAPIError(404, "Not found")
        assert err.status_code == 404
        assert err.message == "Not found"
        assert str(err) == "Not found"

    def test_is_exception(self):
        err = SpaceXAPIError(500, "Internal")
        assert isinstance(err, Exception)


def _make_http_client_mock(request_mock):
    """Create a mock httpx.AsyncClient that works as an async context manager."""
    cm = MagicMock()
    cm.request = request_mock
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=cm)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


class TestSpaceXClientRequest:
    @pytest.mark.asyncio
    async def test_successful_get(self):
        client = SpaceXClient()
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"id": "r1"}]
        mock_resp.raise_for_status = MagicMock()

        request_fn = AsyncMock(return_value=mock_resp)
        ctx = _make_http_client_mock(request_fn)

        with patch("app.clients.spacex_client.httpx.AsyncClient", return_value=ctx):
            result = await client._request("GET", "/v4/rockets")
            assert result == [{"id": "r1"}]

    @pytest.mark.asyncio
    async def test_retries_on_http_error(self):
        client = SpaceXClient()
        client.retries = 1

        error_resp = MagicMock()
        error_resp.status_code = 500
        error_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=error_resp
        )
        ok_resp = MagicMock()
        ok_resp.json.return_value = {"ok": True}
        ok_resp.raise_for_status = MagicMock()

        request_fn = AsyncMock(side_effect=[error_resp, ok_resp])
        ctx = _make_http_client_mock(request_fn)

        with (
            patch("app.clients.spacex_client.httpx.AsyncClient", return_value=ctx),
            patch("app.clients.spacex_client.asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await client._request("GET", "/test")
            assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_raises_after_max_retries_http_error(self):
        client = SpaceXClient()
        client.retries = 0

        error_resp = MagicMock()
        error_resp.status_code = 502
        error_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "bad gateway", request=MagicMock(), response=error_resp
        )

        request_fn = AsyncMock(return_value=error_resp)
        ctx = _make_http_client_mock(request_fn)

        with (
            patch("app.clients.spacex_client.httpx.AsyncClient", return_value=ctx),
            patch("app.clients.spacex_client.asyncio.sleep", new_callable=AsyncMock),
        ):
            with pytest.raises(SpaceXAPIError) as exc:
                await client._request("GET", "/test")
            assert exc.value.status_code == 502

    @pytest.mark.asyncio
    async def test_raises_503_on_connection_error(self):
        client = SpaceXClient()
        client.retries = 0

        request_fn = AsyncMock(side_effect=httpx.RequestError("connection refused"))
        ctx = _make_http_client_mock(request_fn)

        with (
            patch("app.clients.spacex_client.httpx.AsyncClient", return_value=ctx),
            patch("app.clients.spacex_client.asyncio.sleep", new_callable=AsyncMock),
        ):
            with pytest.raises(SpaceXAPIError) as exc:
                await client._request("GET", "/test")
            assert exc.value.status_code == 503


class TestSpaceXClientMethods:
    """Test that each API method calls _request with correct args."""

    @pytest.mark.asyncio
    async def test_get_rockets(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value=[])
        await client.get_rockets()
        client._request.assert_awaited_once_with("GET", "/v4/rockets")

    @pytest.mark.asyncio
    async def test_get_rocket(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value={})
        await client.get_rocket("abc")
        client._request.assert_awaited_once_with("GET", "/v4/rockets/abc")

    @pytest.mark.asyncio
    async def test_get_launches(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value=[])
        await client.get_launches()
        client._request.assert_awaited_once_with("GET", "/v5/launches")

    @pytest.mark.asyncio
    async def test_query_starlink(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value={"docs": []})
        await client.query_starlink(query={"v": "1"}, options={"page": 1})
        client._request.assert_awaited_once_with(
            "POST",
            "/v4/starlink/query",
            json={"query": {"v": "1"}, "options": {"page": 1}},
        )

    @pytest.mark.asyncio
    async def test_get_cores(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value=[])
        await client.get_cores()
        client._request.assert_awaited_once_with("GET", "/v4/cores")

    @pytest.mark.asyncio
    async def test_get_launchpads(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value=[])
        await client.get_launchpads()
        client._request.assert_awaited_once_with("GET", "/v4/launchpads")

    @pytest.mark.asyncio
    async def test_get_latest_launch(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value={})
        await client.get_latest_launch()
        client._request.assert_awaited_once_with("GET", "/v5/launches/latest")

    @pytest.mark.asyncio
    async def test_get_next_launch(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value={})
        await client.get_next_launch()
        client._request.assert_awaited_once_with("GET", "/v5/launches/next")

    @pytest.mark.asyncio
    async def test_get_launch(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value={})
        await client.get_launch("lid")
        client._request.assert_awaited_once_with("GET", "/v5/launches/lid")

    @pytest.mark.asyncio
    async def test_get_payloads_by_ids_empty(self):
        client = SpaceXClient()
        client._request = AsyncMock()
        result = await client.get_payloads_by_ids([])
        assert result == []
        client._request.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_get_payloads_by_ids(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value={"docs": [{"id": "p1"}]})
        result = await client.get_payloads_by_ids(["p1"])
        assert result == [{"id": "p1"}]

    @pytest.mark.asyncio
    async def test_get_crew_by_ids_empty(self):
        client = SpaceXClient()
        client._request = AsyncMock()
        result = await client.get_crew_by_ids([])
        assert result == []

    @pytest.mark.asyncio
    async def test_get_crew_by_ids(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value={"docs": [{"id": "c1"}]})
        result = await client.get_crew_by_ids(["c1"])
        assert result == [{"id": "c1"}]

    @pytest.mark.asyncio
    async def test_get_all_payloads(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value=[])
        await client.get_all_payloads()
        client._request.assert_awaited_once_with("GET", "/v4/payloads")

    @pytest.mark.asyncio
    async def test_get_history(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value=[])
        await client.get_history()
        client._request.assert_awaited_once_with("GET", "/v4/history")

    @pytest.mark.asyncio
    async def test_get_landpads(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value=[])
        await client.get_landpads()
        client._request.assert_awaited_once_with("GET", "/v4/landpads")

    @pytest.mark.asyncio
    async def test_get_roadster(self):
        client = SpaceXClient()
        client._request = AsyncMock(return_value={})
        await client.get_roadster()
        client._request.assert_awaited_once_with("GET", "/v4/roadster")
