"""Pydantic schemas for the real-time notification system."""

from typing import Literal

from pydantic import BaseModel, Field


class NotificationRequest(BaseModel):
    """Inbound notification payload from the sender."""

    type: Literal["success", "warning", "error", "info", "launch"]
    title: str = Field(max_length=100)
    message: str = Field(max_length=500)


class Notification(BaseModel):
    """Full notification object broadcast to connected clients."""

    id: str
    type: str
    title: str
    message: str
    timestamp: str


class NotificationSentResponse(BaseModel):
    """Confirmation returned after publishing a notification."""

    ok: bool
    notification: Notification
