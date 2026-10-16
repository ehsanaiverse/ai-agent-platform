from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    platform: str = Field(default="web")
    platform_user_id: str
    display_name: str
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    response: str