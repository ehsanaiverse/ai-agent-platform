from app.agents.edges.tool_routing import route_after_chat
from app.agents.tools.schemas import ToolCall


def test_route_to_end():
    state = {
        "conversation_id": "1",
        "user_id": "u1",
        "messages": [],
        "latest_message": "Hello",
    }

    assert route_after_chat(state) == "__end__"


def test_route_to_tool_execution():
    state = {
        "conversation_id": "1",
        "user_id": "u1",
        "messages": [],
        "latest_message": "Calculate 2+2",
        "tool_call": ToolCall(
            tool_name="calculator",
            arguments={"expression": "2+2"},
        ),
    }

    assert route_after_chat(state) == "tool_execution"
