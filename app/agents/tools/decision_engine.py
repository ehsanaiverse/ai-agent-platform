"""
Provider-Agnostic Tool Decision Engine.

Responsible for determining whether a tool should be executed based on:
1. Registered tool metadata from ToolRegistry.
2. Provider capabilities (native tool calling vs structured output vs prompt heuristic).
3. Current conversation state.
"""

from __future__ import annotations

from app.agents.state.conversation_state import ConversationState
from app.agents.tools.adapters.factory import ToolAdapterFactory
from app.agents.tools.registry import ToolRegistry
from app.agents.tools.schemas import ToolCall
from app.agents.tools.selector import ToolSelector
from app.llm.providers.base import BaseLLMProvider


class ToolDecisionEngine:
    """
    Evaluates provider capabilities and conversation state to determine tool invocation.

    Acts as a strategy router:
    - Native Tool Calling: if provider.supports_tool_calling() is True
    - Structured Output: if provider.supports_structured_output() is True
    - Fallback Selector: uses rule-based / prompt-driven selection
    """

    def __init__(self, fallback_selector: ToolSelector | None = None) -> None:
        self._fallback_selector = fallback_selector or ToolSelector()

    def decide(
        self,
        state: ConversationState,
        provider: BaseLLMProvider,
        registry: ToolRegistry,
    ) -> ToolCall | None:
        """
        Determine whether a tool should be executed.

        Args:
            state: Active conversation state.
            provider: Active LLM provider interface.
            registry: Central tool registry.

        Returns:
            ToolCall if a tool should be invoked, otherwise None.
        """
        if state.get("tool_result") is not None:
            return None

        tools_metadata = registry.list_metadata()

        if not tools_metadata:
            return self._fallback_selector.select(state)

        if provider.supports_tool_calling():
            return self._decide_native_tool_calling(state, provider, registry)

        if provider.supports_structured_output():
            return self._decide_structured_output(state, provider, registry)

        return self._fallback_selector.select(state)

    def _decide_native_tool_calling(
        self,
        state: ConversationState,
        provider: BaseLLMProvider,
        registry: ToolRegistry,
    ) -> ToolCall | None:
        """
        Decision strategy when the provider natively supports tool calling.
        """
        adapter = ToolAdapterFactory.get_adapter(provider)
        tool_call = adapter.parse_tool_call(state.get("latest_message"))
        if tool_call is not None:
            return tool_call

        return self._fallback_selector.select(state)

    def _decide_structured_output(
        self,
        state: ConversationState,
        provider: BaseLLMProvider,
        registry: ToolRegistry,
    ) -> ToolCall | None:
        """
        Decision strategy when the provider supports structured outputs.
        """
        adapter = ToolAdapterFactory.get_adapter(provider)
        tool_call = adapter.parse_tool_call(state.get("latest_message"))
        if tool_call is not None:
            return tool_call

        return self._fallback_selector.select(state)
