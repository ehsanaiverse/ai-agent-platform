import pytest

from app.agents.tools.adapters.factory import ToolAdapterFactory
from app.agents.tools.adapters.groq_adapter import GroqToolAdapter
from app.agents.tools.metadata import ToolMetadata
from app.agents.tools.parameters import ToolParameter, ToolParameterType
from app.agents.tools.schemas import ToolCall


@pytest.fixture
def groq_adapter() -> GroqToolAdapter:
    return GroqToolAdapter()


@pytest.fixture
def sample_tool_metadata() -> ToolMetadata:
    return ToolMetadata(
        name="calculator",
        description="Evaluates mathematical expressions.",
        parameters=[
            ToolParameter(
                name="expression",
                type=ToolParameterType.STRING,
                description="Mathematical formula to calculate.",
                required=True,
            ),
        ],
    )


def test_format_tools(
    groq_adapter: GroqToolAdapter,
    sample_tool_metadata: ToolMetadata,
) -> None:
    formatted = groq_adapter.format_tools([sample_tool_metadata])

    assert len(formatted) == 1
    tool_def = formatted[0]
    assert tool_def["type"] == "function"
    assert tool_def["function"]["name"] == "calculator"
    assert tool_def["function"]["description"] == "Evaluates mathematical expressions."
    assert "expression" in tool_def["function"]["parameters"]["properties"]
    assert tool_def["function"]["parameters"]["required"] == ["expression"]


def test_parse_tool_call_from_dict(groq_adapter: GroqToolAdapter) -> None:
    dict_payload = {
        "function": {
            "name": "calculator",
            "arguments": '{"expression": "10 + 5"}',
        }
    }

    tool_call = groq_adapter.parse_tool_call(dict_payload)

    assert tool_call is not None
    assert tool_call.tool_name == "calculator"
    assert tool_call.arguments == {"expression": "10 + 5"}


def test_parse_tool_call_from_object_with_tool_calls(
    groq_adapter: GroqToolAdapter,
) -> None:
    class DummyAIMessage:
        tool_calls = [
            {
                "name": "calculator",
                "args": {"expression": "2 * 3"},
            }
        ]

    tool_call = groq_adapter.parse_tool_call(DummyAIMessage())

    assert tool_call is not None
    assert tool_call.tool_name == "calculator"
    assert tool_call.arguments == {"expression": "2 * 3"}


def test_factory_returns_groq_adapter() -> None:
    adapter = ToolAdapterFactory.get_adapter("groq")

    assert isinstance(adapter, GroqToolAdapter)
