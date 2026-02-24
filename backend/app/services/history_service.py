"""Historical milestones service."""

from app.cache.helpers import cached_fetch
from app.clients.spacex_client import spacex_client
from app.config import settings
from app.schemas.history import HistoryEvent, HistoryResponse

CACHE_KEY = "spacex:history"


async def get_history() -> HistoryResponse:
    cached = await cached_fetch(CACHE_KEY, settings.history_ttl, _fetch_history)
    return HistoryResponse(**cached) if isinstance(cached, dict) else cached


async def _fetch_history() -> dict:
    raw = await spacex_client.get_history()

    events = []
    for item in raw:
        links = item.get("links") or {}
        events.append(
            HistoryEvent(
                id=item["id"],
                title=item.get("title", ""),
                event_date_utc=item.get("event_date_utc", ""),
                details=item.get("details"),
                article=links.get("article"),
                wikipedia=links.get("wikipedia"),
            )
        )

    events.sort(key=lambda e: e.event_date_utc)
    response = HistoryResponse(events=events, total=len(events))
    return response.model_dump()
