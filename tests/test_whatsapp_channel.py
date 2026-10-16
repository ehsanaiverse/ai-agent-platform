import hmac
import hashlib
import json
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.channels.schemas import IncomingChannelMessage, OutgoingChannelMessage, ChannelType
from app.channels.whatsapp.adapter import WhatsAppAdapter
from app.channels.whatsapp.client import WhatsAppClient


client = TestClient(app)


def test_whatsapp_verification_success(monkeypatch):
    monkeypatch.setattr(settings, "VERIFY_TOKEN", "test_secret_token")
    
    response = client.get(
        "/api/v1/channels/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test_secret_token",
            "hub.challenge": "123456789",
        },
    )
    assert response.status_code == 200
    assert response.text == "123456789"


def test_whatsapp_verification_invalid_token(monkeypatch):
    monkeypatch.setattr(settings, "VERIFY_TOKEN", "correct_token")
    
    response = client.get(
        "/api/v1/channels/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "123456789",
        },
    )
    assert response.status_code == 403


def test_whatsapp_signature_validation_failure(monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_APP_SECRET", "my_app_secret")
    
    payload = json.dumps({"object": "whatsapp_business_account"}).encode("utf-8")
    
    response = client.post(
        "/api/v1/channels/whatsapp/webhook",
        content=payload,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalid_signature",
        },
    )
    assert response.status_code == 401


def test_whatsapp_webhook_post_flow(monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_APP_SECRET", "")
    
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "contacts": [
                                {
                                    "profile": {"name": "Test User"},
                                    "wa_id": "15551234567",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "15551234567",
                                    "id": "wamid.test_123",
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": "Hello AI"},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    mock_send = AsyncMock(return_value={"messaging_product": "whatsapp", "messages": [{"id": "resp_1"}]})
    mock_read = AsyncMock(return_value=True)

    with patch("app.channels.whatsapp.client.WhatsAppClient.send_text_message", mock_send), \
         patch("app.channels.whatsapp.client.WhatsAppClient.mark_message_as_read", mock_read), \
         patch("app.services.agent_service.AgentService.chat") as mock_chat:
        
        mock_chat.return_value = AsyncMock(
            conversation_id="conv_123",
            response="Hello! How can I assist you today?"
        )
        mock_chat.return_value.response = "Hello! How can I assist you today?"

        response = client.post(
            "/api/v1/channels/whatsapp/webhook",
            json=payload,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["processed_messages"] == 1
