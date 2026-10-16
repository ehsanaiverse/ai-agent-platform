"""
Factory for retrieving provider tool calling adapters.
"""

from __future__ import annotations

from typing import Any

from app.agents.tools.adapters.base import BaseToolAdapter
from app.agents.tools.adapters.groq_adapter import GroqToolAdapter
from app.llm.providers.base import BaseLLMProvider


class ToolAdapterFactory:
    """
    Factory responsible for instantiating and resolving provider tool adapters.
    """

    _adapters: dict[str, BaseToolAdapter] = {
        "groq": GroqToolAdapter(),
    }

    @classmethod
    def get_adapter(cls, provider: str | BaseLLMProvider | Any = "groq") -> BaseToolAdapter:
        """
        Retrieve the appropriate BaseToolAdapter instance.

        Args:
            provider: Provider name string or BaseLLMProvider instance.

        Returns:
            The corresponding BaseToolAdapter (defaults to GroqToolAdapter).
        """
        if isinstance(provider, BaseLLMProvider):
            provider_name = getattr(provider, "name", "groq").lower()
        elif isinstance(provider, str):
            provider_name = provider.lower()
        else:
            provider_name = "groq"

        return cls._adapters.get(provider_name, cls._adapters["groq"])
