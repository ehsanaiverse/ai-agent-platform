from app.agents.prompts import PromptManager
from app.llm.schemas import LLMMessage
from app.llm.schemas import MessageRole


class PromptComposer:
    """
    Builds the final list of messages sent to the LLM.

    Responsibilities:
    - Retrieve prompt assets from PromptManager.
    - Combine system instructions.
    - Preserve conversation history.
    - Return a complete message list for the LLM.

    This class does NOT:
    - Call the LLM.
    - Know about LangGraph.
    - Know about FastAPI.
    - Access the database.
    """

    def __init__(self) -> None:
        self._prompt_manager = PromptManager()

    def compose(
        self,
        conversation: list[LLMMessage],
    ) -> list[LLMMessage]:
        """
        Compose the final prompt sent to the LLM.
        """

        system_prompt = "\n\n".join(
            [
                self._prompt_manager.get_system_prompt(),
                self._prompt_manager.get_chat_prompt(),
            ]
        )

        return [
            LLMMessage(
                role=MessageRole.SYSTEM,
                content=system_prompt,
            ),
            *conversation,
        ]