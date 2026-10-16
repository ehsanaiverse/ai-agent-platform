from app.llm.factory import LLMFactory
from app.llm.providers.base import BaseLLMProvider


def get_llm_provider() -> BaseLLMProvider:
    return LLMFactory.create_provider()