"""
Runtime builder.

Responsible for assembling the runtime dependencies required
by the LangGraph workflow.
"""

from app.agents.composer.prompt_composer import PromptComposer
from app.agents.runtime.context import AgentContext
from app.agents.tools.decision_engine import ToolDecisionEngine
from app.agents.tools.implementations import (
    CalculatorTool,
    DateTimeTool,
    HTTPTool,
    SearchTool,
)
from app.agents.tools.registry import ToolRegistry
from app.llm.providers.base import BaseLLMProvider


class RuntimeBuilder:
    """
    Factory responsible for constructing AgentContext.

    This centralizes runtime dependency creation so that
    AgentRunner focuses only on executing the workflow.
    """

    @staticmethod
    def build(
        llm_provider: BaseLLMProvider,
    ) -> AgentContext:
        """
        Build and return a fully initialized AgentContext.
        """

        tool_registry = ToolRegistry()
        tool_registry.register(CalculatorTool())
        tool_registry.register(DateTimeTool())
        tool_registry.register(HTTPTool())
        tool_registry.register(SearchTool())

        return AgentContext(
            llm_provider=llm_provider,
            prompt_composer=PromptComposer(),
            tool_registry=tool_registry,
            tool_decision_engine=ToolDecisionEngine(),
        )