from app.agents.prompts.chat import ChatPrompt
from app.agents.prompts.system import SystemPrompt


class PromptManager:
    """
    Central access point for prompt providers.
    """

    def __init__(self):
        self._system = SystemPrompt()
        self._chat = ChatPrompt()

    def get_system_prompt(self) -> str:
        return self._system.get_prompt()

    def get_chat_prompt(self) -> str:
        return self._chat.get_prompt()