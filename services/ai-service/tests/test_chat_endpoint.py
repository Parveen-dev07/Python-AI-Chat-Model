from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_chat_requires_api_key(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/chat",
        json={"widget_id": "demo-widget", "message": "Hello"},
    )
    assert resp.status_code == 401


def test_chat_success(client: TestClient) -> None:
    with patch("app.api.routes.chat.ChatService") as mock_service_cls:
        instance = mock_service_cls.return_value
        instance.answer_question = AsyncMock(
            return_value=("The Demo Burger costs 199.", "req-1")
        )
        resp = client.post(
            "/api/v1/chat",
            json={"widget_id": "demo-widget", "message": "Price of Demo Burger?"},
            headers={"X-API-Key": "test-api-key"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"] == "The Demo Burger costs 199."
    assert body["request_id"] == "req-1"


def test_chat_unknown_widget(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/chat",
        json={"widget_id": "unknown", "message": "Hi"},
        headers={"X-API-Key": "test-api-key"},
    )
    assert resp.status_code == 403
