"""Tests for the notification system (schema, service, routes)."""

from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.notifications import Notification, NotificationRequest
from app.services.notification_service import publish


class TestNotificationSchema:
    def test_valid_request(self):
        req = NotificationRequest(
            type="launch",
            title="Falcon 9 Liftoff",
            message="Starlink 6-42 launched from LC-39A",
        )
        assert req.type == "launch"
        assert req.title == "Falcon 9 Liftoff"

    def test_all_types_valid(self):
        for t in ("success", "warning", "error", "info", "launch"):
            req = NotificationRequest(type=t, title="Test", message="msg")
            assert req.type == t

    def test_invalid_type_rejected(self):
        with pytest.raises(Exception):
            NotificationRequest(type="unknown", title="Bad", message="nope")

    def test_title_max_length(self):
        with pytest.raises(Exception):
            NotificationRequest(type="info", title="x" * 101, message="ok")

    def test_message_max_length(self):
        with pytest.raises(Exception):
            NotificationRequest(type="info", title="ok", message="x" * 501)

    def test_notification_model(self):
        n = Notification(
            id="abc",
            type="success",
            title="Done",
            message="All good",
            timestamp="2025-01-01T00:00:00Z",
        )
        assert n.id == "abc"


class TestNotificationService:
    @pytest.mark.asyncio
    async def test_publish_sends_to_redis(self):
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        with patch("app.services.notification_service.cache") as mock_cache:
            mock_cache._redis = mock_redis

            req = NotificationRequest(
                type="launch",
                title="Test Launch",
                message="Falcon 9 lifted off",
            )
            result = await publish(req)

            assert result.type == "launch"
            assert result.title == "Test Launch"
            assert result.id
            assert result.timestamp
            mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_without_redis(self):
        with patch("app.services.notification_service.cache") as mock_cache:
            mock_cache._redis = None

            req = NotificationRequest(
                type="info",
                title="Test",
                message="No Redis",
            )
            result = await publish(req)

            assert result.type == "info"
            assert result.id


class TestNotificationRoutes:
    @pytest.mark.asyncio
    async def test_send_notification(self, client):
        with patch("app.services.notification_service.cache") as mock_cache:
            mock_redis = AsyncMock()
            mock_redis.publish = AsyncMock()
            mock_cache._redis = mock_redis

            resp = await client.post(
                "/api/notifications/send",
                json={
                    "type": "success",
                    "title": "Mission Complete",
                    "message": "Payload deployed",
                },
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["ok"] is True
            assert body["notification"]["type"] == "success"
            assert body["notification"]["id"]

    @pytest.mark.asyncio
    async def test_send_invalid_type(self, client):
        resp = await client.post(
            "/api/notifications/send",
            json={
                "type": "invalid",
                "title": "Bad",
                "message": "Nope",
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_stream_endpoint_returns_sse(self, client):
        async def mock_subscribe():
            yield (
                'data: {"id":"1","type":"info",'
                '"title":"T","message":"M",'
                '"timestamp":"2025-01-01T00:00:00Z"}\n\n'
            )

        with patch(
            "app.services.notification_service.subscribe",
            return_value=mock_subscribe(),
        ):
            resp = await client.get("/api/notifications/stream")
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get("content-type", "")
