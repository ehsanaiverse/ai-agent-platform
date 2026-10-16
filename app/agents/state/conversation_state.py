from typing import NotRequired

from typing_extensions import TypedDict

from app.agents.tools.schemas import ToolCall, ToolResult
from app.llm.schemas import LLMMessage


class ConversationState(TypedDict):
    """
    Shared state flowing through the LangGraph workflow.
    """

    conversation_id: str
    user_id: str

    # Complete conversation history
    messages: list[LLMMessage]

    # Latest user message
    latest_message: str

    # Final assistant response
    response: NotRequired[str]

    # Requested tool (if any)
    tool_call: NotRequired[ToolCall | None]

    # Tool execution result
    tool_result: NotRequired[ToolResult | None]