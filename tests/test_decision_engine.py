import pytest

from app.agents.state.conversation_state import ConversationState
from app.agents.tools.base import BaseTool
from app.agents.tools.decision_engine import ToolDecisionEngine
from app.agents.tools.registry import ToolRegistry
from app.agents.tools.schemas import ToolCall, ToolResult
from app.llm.capabilities import LLMCapabilities
from tests.fixtures.llm import DummyLLMProvider


class DummyTool(BaseTool):
    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Echo tool"

    async def execute(self, call: ToolCall) -> ToolResult:
        return ToolResult(success=True, output="echoed")


class CapabilityLLMProvider(DummyLLMProvider):
    def __init__(self, capabilities: LLMCapabilities) -> None:
        self._capabilities = capabilities

    @property
    def capabilities(self) -> LLMCapabilities:
        return self._capabilities


@pytest.fixture
def registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(DummyTool())
    return reg


@pytest.fixture
def decision_engine() -> ToolDecisionEngine:
    return ToolDecisionEngine()


def test_decide_with_rule_trigger(
    registry: ToolRegistry,
    decision_engine: ToolDecisionEngine,
) -> None:
    provider = DummyLLMProvider()
    state: ConversationState = {
        "messages": [],
        "latest_message": "/tool hello world",
    }

    tool_call = decision_engine.decide(state, provider, registry)

    assert tool_call is not None
    assert tool_call.tool_name == "echo"
    assert tool_call.arguments["message"] == "/tool hello world"


def test_decide_with_native_tool_calling_capability(
    registry: ToolRegistry,
    decision_engine: ToolDecisionEngine,
) -> None:
    capabilities = LLMCapabilities(tool_calling=True)
    provider = CapabilityLLMProvider(capabilities)
    state: ConversationState = {
        "messages": [],
        "latest_message": "What is the weather?",
    }

    tool_call = decision_engine.decide(state, provider, registry)
    # Native tool calling strategy evaluates prompt/state; without rule trigger, returns None
    assert tool_call is None


def test_decide_with_structured_output_capability(
    registry: ToolRegistry,
    decision_engine: ToolDecisionEngine,
) -> None:
    capabilities = LLMCapabilities(structured_output=True)
    provider = CapabilityLLMProvider(capabilities)
    state: ConversationState = {
        "messages": [],
        "latest_message": "Calculate 2+2",
    }

    tool_call = decision_engine.decide(state, provider, registry)
    assert tool_call is None
