import pytest

from app.agents.composer.prompt_composer import PromptComposer
from app.agents.nodes.tool_execution import tool_execution_node
from app.agents.runtime.context import AgentContext
from app.agents.state.conversation_state import ConversationState
from app.agents.tools.base import BaseTool
from app.agents.tools.decision_engine import ToolDecisionEngine
from app.agents.tools.metadata import ToolMetadata
from app.agents.tools.parameters import ToolParameter, ToolParameterType
from app.agents.tools.registry import ToolRegistry
from app.agents.tools.schemas import ToolCall, ToolResult
from tests.fixtures.llm import DummyLLMProvider


class DummyRuntime:
    def __init__(self, context: AgentContext):
        self.context = context


class EchoTool(BaseTool):

    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Echo Tool"

    async def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:

        return ToolResult(
            success=True,
            output="Echo executed",
        )

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=[
                ToolParameter(
                    name="message",
                    type=ToolParameterType.STRING,
                    description="Message to echo.",
                    required=True,
                )
            ],
        )


@pytest.mark.asyncio
async def test_tool_execution_without_tool_call():

    context = AgentContext(
        llm_provider=DummyLLMProvider(),
        prompt_composer=PromptComposer(),
        tool_registry=ToolRegistry(),
        tool_decision_engine=ToolDecisionEngine(),
    )

    runtime = DummyRuntime(context)

    state: ConversationState = {
        "conversation_id": "1",
        "user_id": "user-1",
        "messages": [],
        "latest_message": "Hello",
    }

    result = await tool_execution_node(
        state,
        runtime,
    )

    assert result == {}


@pytest.mark.asyncio
async def test_tool_execution_success():

    registry = ToolRegistry()
    registry.register(EchoTool())

    context = AgentContext(
        llm_provider=DummyLLMProvider(),
        prompt_composer=PromptComposer(),
        tool_registry=registry,
        tool_decision_engine=ToolDecisionEngine(),
    )

    runtime = DummyRuntime(context)

    state: ConversationState = {
        "conversation_id": "1",
        "user_id": "user-1",
        "messages": [],
        "latest_message": "Hello",
        "tool_call": ToolCall(
            tool_name="echo",
            arguments={},
        ),
    }

    result = await tool_execution_node(
        state,
        runtime,
    )

    assert result["tool_result"].success is True
    assert result["tool_result"].output == "Echo executed"
    assert result["tool_call"] is None
