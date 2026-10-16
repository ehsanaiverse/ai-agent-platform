from app.agents.tools.selector import ToolSelector
from app.agents.tools.schemas import ToolCall


def test_selector_returns_none_for_normal_message():
    """
    Normal messages should not request a tool.
    """

    selector = ToolSelector()

    state = {
        "conversation_id": "conversation-1",
        "user_id": "user-1",
        "messages": [],
        "latest_message": "Hello, how are you?",
    }

    result = selector.select(state)

    assert result is None


def test_selector_returns_tool_call():
    """
    Messages beginning with '/tool' should request the echo tool.
    """

    selector = ToolSelector()

    state = {
        "conversation_id": "conversation-1",
        "user_id": "user-1",
        "messages": [],
        "latest_message": "/tool Hello World",
    }

    result = selector.select(state)

    assert isinstance(result, ToolCall)
    assert result.tool_name == "echo"
    assert result.arguments == {
        "message": "/tool Hello World",
    }