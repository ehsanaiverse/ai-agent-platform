from app.llm.capabilities import LLMCapabilities
from app.llm.providers.base import BaseLLMProvider
from app.llm.schemas import LLMMessage, LLMResponse


class DummyLLMProvider(BaseLLMProvider):
    """
    Test double for BaseLLMProvider.

    This implementation never calls a real LLM and always
    returns a predictable response.
    """

    @property
    def capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            streaming=False,
            tool_calling=False,
            structured_output=False,
            vision=False,
        )

    async def generate(
        self,
        messages: list[LLMMessage],
    ) -> LLMResponse:
        return LLMResponse(
            content="Dummy response",
            model="dummy-model",
        )