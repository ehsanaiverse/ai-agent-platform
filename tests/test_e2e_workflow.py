import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_e2e_chat_workflow(client: TestClient) -> None:
    payload = {
        "platform": "web",
        "platform_user_id": "test_user_001",
        "display_name": "Test User",
        "message": "Hello! What is your name?",
    }

    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    assert len(data["response"]) > 0


def test_e2e_tool_execution_workflow(client: TestClient) -> None:
    payload = {
        "platform": "web",
        "platform_user_id": "test_user_001",
        "display_name": "Test User",
        "message": "/tool Calculate 25 * 4",
    }

    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
