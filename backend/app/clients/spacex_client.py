"""HTTP client for the SpaceX REST API with retry logic."""

import asyncio

import httpx

from app.config import settings


class SpaceXAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class SpaceXClient:
    def __init__(self):
        self.base_url = settings.spacex_api_base
        self.timeout = settings.spacex_timeout
        self.retries = settings.spacex_retries

    async def _request(self, method: str, path: str, **kwargs) -> dict | list:
        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(method, f"{self.base_url}{path}", **kwargs)
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPStatusError as exc:
                if attempt == self.retries:
                    raise SpaceXAPIError(exc.response.status_code, str(exc))
            except httpx.RequestError as exc:
                if attempt == self.retries:
                    raise SpaceXAPIError(503, f"SpaceX API unavailable: {exc}")
            await asyncio.sleep(2**attempt)

    async def get_rockets(self) -> list[dict]:
        return await self._request("GET", "/v4/rockets")

    async def get_rocket(self, rocket_id: str) -> dict:
        return await self._request("GET", f"/v4/rockets/{rocket_id}")

    async def get_launches(self) -> list[dict]:
        return await self._request("GET", "/v5/launches")

    async def query_starlink(self, query: dict | None = None, options: dict | None = None) -> dict:
        body = {"query": query or {}, "options": options or {}}
        return await self._request("POST", "/v4/starlink/query", json=body)

    async def get_cores(self) -> list[dict]:
        return await self._request("GET", "/v4/cores")

    async def get_launchpads(self) -> list[dict]:
        return await self._request("GET", "/v4/launchpads")

    async def get_latest_launch(self) -> dict:
        return await self._request("GET", "/v5/launches/latest")

    async def get_next_launch(self) -> dict:
        return await self._request("GET", "/v5/launches/next")

    async def get_launch(self, launch_id: str) -> dict:
        return await self._request("GET", f"/v5/launches/{launch_id}")

    async def get_payloads_by_ids(self, ids: list[str]) -> list[dict]:
        if not ids:
            return []
        body = {"query": {"_id": {"$in": ids}}, "options": {"pagination": False}}
        result = await self._request("POST", "/v4/payloads/query", json=body)
        return result.get("docs", [])

    async def get_crew_by_ids(self, ids: list[str]) -> list[dict]:
        if not ids:
            return []
        body = {"query": {"_id": {"$in": ids}}, "options": {"pagination": False}}
        result = await self._request("POST", "/v4/crew/query", json=body)
        return result.get("docs", [])

    async def get_all_payloads(self) -> list[dict]:
        return await self._request("GET", "/v4/payloads")

    async def get_history(self) -> list[dict]:
        return await self._request("GET", "/v4/history")

    async def get_landpads(self) -> list[dict]:
        return await self._request("GET", "/v4/landpads")

    async def get_roadster(self) -> dict:
        return await self._request("GET", "/v4/roadster")


spacex_client = SpaceXClient()
