"""
AgentRunner.

Responsible for executing the compiled LangGraph workflow.

This class should remain independent of:
- FastAPI
- SQLAlchemy
- Messaging channels
- Business services
"""

from app.agents.graph.builder import GraphBuilder
from app.agents.state.conversation_state import ConversationState
from app.llm.providers.base import BaseLLMProvider
from app.agents.runtime.builder import RuntimeBuilder

class AgentRunner:
    """
    Executes the AI workflow.
    """

    def __init__(self, llm_provider: BaseLLMProvider) -> None:
        
        self._context = RuntimeBuilder.build(
        llm_provider=llm_provider,
    )
        
        self._graph = GraphBuilder.build()


    async def run(
        self,
        state: ConversationState,
    ) -> ConversationState:
        """
        Execute the LangGraph workflow.
        """
        
        thread_id = state["conversation_id"]

        result = await self._graph.ainvoke(
            state,
            context=self._context,
            config={
                "configurable": {
                    "thread_id": thread_id,
                }
            },
        )

        return result