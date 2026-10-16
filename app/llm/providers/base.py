from abc import ABC, abstractmethod

from app.llm.schemas import LLMMessage
from app.llm.schemas import LLMResponse
from app.llm.capabilities import LLMCapabilities


class BaseLLMProvider(ABC):
    """
    Base interface for all LLM providers.
    """

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
    ) -> LLMResponse:
        """
        Generate a response from the provider.
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def capabilities(self) -> LLMCapabilities:
        """
        Capabilities supported by this provider.
        """
        raise NotImplementedError
    
    def supports_streaming(self) -> bool:
        return self.capabilities.streaming


    def supports_tool_calling(self) -> bool:
        return self.capabilities.tool_calling


    def supports_structured_output(self) -> bool:
        return self.capabilities.structured_output


    def supports_vision(self) -> bool:
        return self.capabilities.vision