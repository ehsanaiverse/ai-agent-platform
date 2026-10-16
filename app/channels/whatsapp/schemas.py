from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WhatsAppProfile(BaseModel):
    name: Optional[str] = None


class WhatsAppContact(BaseModel):
    profile: Optional[WhatsAppProfile] = None
    wa_id: Optional[str] = None


class WhatsAppTextMessage(BaseModel):
    body: Optional[str] = None


class WhatsAppMessage(BaseModel):
    id: str
    from_user: str = Field(..., alias="from")
    timestamp: Optional[str] = None
    type: str = "text"
    text: Optional[WhatsAppTextMessage] = None

    model_config = {
        "populate_by_name": True,
    }


class WhatsAppValue(BaseModel):
    messaging_product: Optional[str] = None
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessage]] = None
    statuses: Optional[List[Dict[str, Any]]] = None


class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: Optional[str] = None


class WhatsAppEntry(BaseModel):
    id: Optional[str] = None
    changes: List[WhatsAppChange] = Field(default_factory=list)


class WhatsAppWebhookPayload(BaseModel):
    object: Optional[str] = None
    entry: List[WhatsAppEntry] = Field(default_factory=list)
