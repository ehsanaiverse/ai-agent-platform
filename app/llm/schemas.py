# LLM data models
from enum import Enum

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class LLMMessage(BaseModel):
    role: MessageRole
    content: str = Field(default="")


class LLMResponse(BaseModel):
    content: str
    model: str