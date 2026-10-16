"""
Base abstraction for all agent tools.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from app.agents.tools.metadata import ToolMetadata
from app.agents.tools.schemas import ToolCall
from app.agents.tools.schemas import ToolResult


class BaseTool(ABC):
    """
    Base interface implemented by every tool.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique tool identifier.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable tool description.
        """
        raise NotImplementedError

    @property
    def metadata(self) -> ToolMetadata:
        """
        Structured description of this tool.

        This metadata is provider-agnostic and can later be
        transformed into OpenAI, Anthropic, Groq, Gemini,
        or other provider-specific tool definitions.
        """
        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=[],
        )

    @abstractmethod
    async def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:
        """
        Execute the requested tool.
        """
        raise NotImplementedError