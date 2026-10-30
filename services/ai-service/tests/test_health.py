from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_database_health_ok(client: TestClient) -> None:
    with patch("app.api.routes.health.PostgresConnector") as mock_cls:
        instance = MagicMock()
        mock_cls.return_value = instance
        resp = client.get("/health/database")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    instance.connect.assert_called_once()
    instance.ping.assert_called_once()
    instance.close.assert_called_once()


def test_ai_health(client: TestClient) -> None:
    with patch("app.api.routes.health.create_provider") as mock_create:
        provider = MagicMock()
        provider.supports_tool_calling.return_value = True
        provider.check_ready = AsyncMock(return_value=(True, "ok"))
        mock_create.return_value = provider
        resp = client.get("/api/v1/health/ai")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["provider"] == "gemini"
