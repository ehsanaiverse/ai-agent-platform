"""
Tool execution node.

Responsible for executing tool calls produced by other nodes.

This node:
- reads ToolCall from the graph state
- retrieves the tool from ToolRegistry
- executes the tool
- stores ToolResult back into the state

It never performs LLM reasoning.
"""

import asyncio
from langgraph.runtime import Runtime

from app.agents.runtime.context import AgentContext
from app.agents.state.conversation_state import ConversationState
from app.agents.tools.exceptions import ToolError
from app.agents.tools.schemas import ToolResult
from app.core.config import settings


async def tool_execution_node(
    state: ConversationState,
    runtime: Runtime[AgentContext],
) -> dict:
    """
    Execute a tool requested by the workflow.

    Parameters
    ----------
    state:
        Current graph state.

    runtime:
        LangGraph runtime providing AgentContext.

    Returns
    -------
    dict
        Updated state containing ToolResult and setting tool_call to None.
    """

    tool_call = state.get("tool_call")

    if tool_call is None:
        return {}

    registry = runtime.context.tool_registry

    try:
        tool = registry.get(tool_call.tool_name)

        result = await asyncio.wait_for(
            tool.execute(tool_call),
            timeout=float(settings.TOOL_EXECUTION_TIMEOUT),
        )

    except asyncio.TimeoutError:
        result = ToolResult(
            success=False,
            output="",
            error=f"Tool '{tool_call.tool_name}' timed out after {settings.TOOL_EXECUTION_TIMEOUT}s.",
        )
    except ToolError as exc:
        result = ToolResult(
            success=False,
            output="",
            error=str(exc),
        )
    except Exception as exc:
        result = ToolResult(
            success=False,
            output="",
            error=f"Unexpected error executing tool '{tool_call.tool_name}': {exc}",
        )

    return {
        "tool_result": result,
        "tool_call": None,
    }