"""
LangGraph builder.

Responsible for constructing and compiling the conversation graph.
"""

from langgraph.graph import END, START, StateGraph

from app.agents.edges.tool_routing import route_after_chat
from app.agents.memory.checkpointer import checkpointer
from app.agents.nodes.chat import chat_node
from app.agents.nodes.tool_execution import tool_execution_node
from app.agents.state.conversation_state import ConversationState


class GraphBuilder:
    """
    Builds and compiles the conversation workflow.
    """

    @staticmethod
    def build():
        workflow = StateGraph(ConversationState)

        # Register nodes
        workflow.add_node("chat", chat_node)
        workflow.add_node("tool_execution", tool_execution_node)

        # Start -> Chat
        workflow.add_edge(START, "chat")

        # Chat -> Conditional Routing
        workflow.add_conditional_edges(
            "chat",
            route_after_chat,
            {
                "tool_execution": "tool_execution",
                "__end__": END,
            },
        )

        # Tool -> Chat
        workflow.add_edge(
            "tool_execution",
            "chat",
        )

        return workflow.compile(
            checkpointer=checkpointer,
        )