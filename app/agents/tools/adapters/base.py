"""
Base interface for provider tool adapters.

Adapters translate provider-agnostic ToolMetadata into provider-specific schemas
(e.g., OpenAI Function Calling, Anthropic Tool Use) and parse provider response payloads.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.agents.tools.metadata import ToolMetadata
from app.agents.tools.schemas import ToolCall


class BaseToolAdapter(ABC):
    """
    Abstract interface for provider-specific tool schema adapters.
    """

    @abstractmethod
    def format_tools(self, tools: list[ToolMetadata]) -> list[dict[str, Any]]:
        """
        Convert standard ToolMetadata instances into provider-specific tool definitions.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_tool_call(self, response: Any) -> ToolCall | None:
        """
        Parse raw provider response payload into a standardized ToolCall object.
        """
        raise NotImplementedError
