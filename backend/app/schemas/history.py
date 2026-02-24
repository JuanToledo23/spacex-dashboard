"""Pydantic schemas for historical milestones."""

from pydantic import BaseModel


class HistoryEvent(BaseModel):
    id: str
    title: str
    event_date_utc: str
    details: str | None = None
    article: str | None = None
    wikipedia: str | None = None


class HistoryResponse(BaseModel):
    events: list[HistoryEvent]
    total: int
