# LLM client factory
from app.core.config import settings
from app.llm.providers.base import BaseLLMProvider
from app.llm.providers.groq_provider import GroqProvider


class LLMFactory:
    """
    Factory responsible for creating the configured LLM provider.
    """

    @staticmethod
    def create_provider() -> BaseLLMProvider:
        provider = settings.LLM_PROVIDER.lower()

        if provider == "groq":
            return GroqProvider()

        raise ValueError(
            f"Unsupported LLM provider: {settings.LLM_PROVIDER}"
        )