from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ChannelType(str, Enum):
    """Supported communication channels."""
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    WEB = "web"


class MessageType(str, Enum):
    """Supported message content types across channels."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"
    UNKNOWN = "unknown"


class IncomingChannelMessage(BaseModel):
    """
    Provider-independent model for incoming messages received from any communication channel.
    
    Acts as the standard contract between adapter layers and application services.
    """
    channel: ChannelType = Field(..., description="Source communication channel")
    sender_id: str = Field(..., description="Unique sender identifier on the channel (e.g. phone number, user ID)")
    display_name: str = Field(default="User", description="Sender's display or profile name if available")
    conversation_id: Optional[str] = Field(default=None, description="Channel conversation ID if applicable")
    message_id: str = Field(..., description="Unique message ID provided by the channel platform")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Type of message payload")
    text: str = Field(..., description="Normalized plain text content of the message")
    timestamp: Optional[int] = Field(default=None, description="Unix timestamp from source provider")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Channel-specific non-sensitive metadata")


class OutgoingChannelMessage(BaseModel):
    """
    Provider-independent model for outgoing messages sent to any communication channel.
    """
    recipient_id: str = Field(..., description="Target recipient ID on the platform (e.g. recipient phone number)")
    text: str = Field(..., description="Text content to transmit")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Type of outgoing message")
    reply_to_message_id: Optional[str] = Field(default=None, description="Original message ID to reference in context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional vendor-specific transmission flags")
