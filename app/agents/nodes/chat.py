"""
Chat node.

This node is responsible for generating an AI response.

Responsibilities:
- Read conversation state
- Call the configured LLM provider
- Return updated state
"""

from typing import Any

from app.agents.runtime.context import AgentContext
from app.agents.state.conversation_state import ConversationState
from app.llm.schemas import LLMMessage
from app.llm.schemas import MessageRole


async def chat_node(
    state: ConversationState,
    runtime: Any,
) -> dict:
    """
    Generate an AI response.
    """

    context: AgentContext

    if hasattr(runtime, "context"):
        context = runtime.context
    else:
        context = runtime

    if not isinstance(context, AgentContext):
        raise TypeError(
            "Expected runtime context to be an AgentContext instance."
        )

    tool_result = state.get("tool_result")

    # If a tool was executed in the previous step, append tool output to context
    input_messages = list(state["messages"])
    if tool_result is not None:
        tool_output_str = tool_result.output if tool_result.success else f"Error: {tool_result.error}"
        input_messages.append(
            LLMMessage(
                role=MessageRole.SYSTEM,
                content=f"[Tool Execution Result]: {tool_output_str}",
            )
        )

    messages = context.prompt_composer.compose(input_messages)

    response = await context.llm_provider.generate(messages)

    # If tool_result was present, we already executed a tool for this turn
    if tool_result is not None:
        final_content = response.content
        if not final_content and tool_result.success:
            final_content = f"Tool output: {tool_result.output}"

        return {
            "response": final_content,
            "messages": [
                *state["messages"],
                LLMMessage(
                    role=MessageRole.ASSISTANT,
                    content=final_content,
                ),
            ],
            "tool_call": None,
            "tool_result": None,
        }

    tool_call = context.tool_decision_engine.decide(
        state,
        context.llm_provider,
        context.tool_registry,
    )

    result = {
        "response": response.content,
        "messages": [
            *state["messages"],
            LLMMessage(
                role=MessageRole.ASSISTANT,
                content=response.content,
            ),
        ],
        "tool_call": tool_call,
        "tool_result": None,
    }

    return result