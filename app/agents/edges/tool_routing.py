"""
Routing logic for the Tool Framework.

These functions determine which node should execute next
based on the current graph state.
"""

from typing import Literal

from app.agents.state.conversation_state import ConversationState


def route_after_chat(
    state: ConversationState,
) -> Literal["tool_execution", "__end__"]:
    """
    Determine whether the workflow should execute a tool.

    Returns:
        - "tool_execution" if a tool has been requested.
        - "__end__" otherwise.
    """

    tool_call = state.get("tool_call")

    if tool_call is None:
        return "__end__"

    return "tool_execution"