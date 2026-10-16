"""
Tool selection.

Determines whether a tool should be requested based on
the current conversation state.

This initial implementation uses simple heuristics.
It will later be replaced with LLM-driven tool selection.
"""

from app.agents.state.conversation_state import ConversationState
from app.agents.tools.schemas import ToolCall


class ToolSelector:
    """
    Determines whether a tool should be invoked.
    """

    def select(
        self,
        state: ConversationState,
    ) -> ToolCall | None:
        """
        Decide whether a tool is needed.

        Returns:
            ToolCall if a tool should be executed,
            otherwise None.
        """

        if state.get("tool_result") is not None:
            return None

        raw_message = state.get("latest_message", "").strip()
        message_lower = raw_message.lower()

        if message_lower.startswith("/tool"):
            payload = raw_message[5:].strip()
            if not payload:
                return None

            parts = payload.split(maxsplit=1)
            tool_target = parts[0].lower()
            arg_str = parts[1] if len(parts) > 1 else ""

            if tool_target in ("calculator", "calc"):
                return ToolCall(
                    tool_name="calculator",
                    arguments={"expression": arg_str},
                )
            elif tool_target in ("datetime", "time", "date"):
                return ToolCall(
                    tool_name="datetime",
                    arguments={"timezone": arg_str or "UTC"},
                )
            elif tool_target in ("web_search", "search"):
                return ToolCall(
                    tool_name="web_search",
                    arguments={"query": arg_str},
                )
            elif tool_target in ("http_client", "http"):
                return ToolCall(
                    tool_name="http_client",
                    arguments={"url": arg_str},
                )
            elif tool_target in ("echo", "hello"):
                return ToolCall(
                    tool_name="echo",
                    arguments={"message": raw_message},
                )
            else:
                return ToolCall(
                    tool_name="echo",
                    arguments={"message": raw_message},
                )

        return None