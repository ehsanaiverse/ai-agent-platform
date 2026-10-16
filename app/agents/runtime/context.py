from dataclasses import dataclass

from app.agents.composer.prompt_composer import PromptComposer
from app.agents.tools.decision_engine import ToolDecisionEngine
from app.agents.tools.registry import ToolRegistry
from app.llm.providers.base import BaseLLMProvider


@dataclass(slots=True)
class AgentContext:
    """
    Runtime dependencies shared across LangGraph nodes.

    This object is created once per AgentRunner and passed
    to every node during graph execution.
    """

    llm_provider: BaseLLMProvider
    prompt_composer: PromptComposer
    tool_registry: ToolRegistry
    tool_decision_engine: ToolDecisionEngine