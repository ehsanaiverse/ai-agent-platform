from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq

from app.core.config import settings
from app.llm.providers.base import BaseLLMProvider
from app.llm.schemas import LLMMessage
from app.llm.schemas import LLMResponse
from app.llm.schemas import MessageRole
from app.llm.capabilities import LLMCapabilities


class GroqProvider(BaseLLMProvider):
    """
    Groq implementation of the LLM provider interface.
    """

    def __init__(self) -> None:
        self._client = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0,
        )

    @staticmethod
    def _convert_messages(messages: list[LLMMessage]):
        """
        Convert platform messages into LangChain messages.
        """
        converted = []

        for message in messages:
            if message.role == MessageRole.SYSTEM:
                converted.append(SystemMessage(content=message.content))

            elif message.role == MessageRole.USER:
                converted.append(HumanMessage(content=message.content))

            elif message.role == MessageRole.ASSISTANT:
                converted.append(AIMessage(content=message.content))

        return converted
    
    @property
    def capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            streaming=True,
            tool_calling=True,
            structured_output=True,
            vision=False,
        )

    async def generate(
        self,
        messages: list[LLMMessage],
    ) -> LLMResponse:
        """
        Generate a response using Groq.
        """
        langchain_messages = self._convert_messages(messages)

        response = await self._client.ainvoke(langchain_messages)

        return LLMResponse(
            content=response.content,
            model=settings.GROQ_MODEL,
        )