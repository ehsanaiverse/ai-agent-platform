from __future__ import annotations

from app.agents.tools.base import BaseTool
from app.agents.tools.exceptions import (
    DuplicateToolRegistrationError,
    InvalidToolError,
    ToolNotFoundError,
)

from app.agents.tools.metadata import ToolMetadata


class ToolRegistry:
    """
    Central registry responsible for managing tool instances.

    The registry owns:
    - Tool registration
    - Tool lookup
    - Listing available tools

    It does NOT execute orchestration logic.
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool instance.

        Raises:
            InvalidToolError:
                If the provided object is not a BaseTool.

            DuplicateToolRegistrationError:
                If a tool with the same name already exists.
        """

        if not isinstance(tool, BaseTool):
            raise InvalidToolError(
                f"{tool!r} is not a valid BaseTool."
            )

        if tool.name in self._tools:
            raise DuplicateToolRegistrationError(tool.name)

        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """
        Retrieve a registered tool by name.
        """

        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(name) from exc
        
        
    def get_metadata(self, name: str) -> ToolMetadata:
        """
        Retrieve metadata for a registered tool.

        This allows provider integrations to inspect tool
        descriptions without accessing executable instances.
        """

        return self.get(name).metadata


    def list_metadata(self) -> list[ToolMetadata]:
        """
        Return metadata for every registered tool.

        The returned metadata is provider-agnostic and will later
        be transformed into provider-specific schemas such as:

        - OpenAI Function Calling
        - Anthropic Tool Use
        - Gemini Function Calling
        - Groq Structured Outputs
        """

        return [
            tool.metadata
            for tool in self._tools.values()
        ]


    def has(self, name: str) -> bool:
        """
        Return True if a tool is registered.
        """

        return name in self._tools

    def list_tools(self) -> list[str]:
        """
        Return all registered tool names.
        """

        return sorted(self._tools.keys())

    def unregister(self, name: str) -> None:
        """
        Remove a tool from the registry.

        Raises:
            ToolNotFoundError
        """

        if not self.has(name):
            raise ToolNotFoundError(name)

        del self._tools[name]

    def clear(self) -> None:
        """
        Remove all registered tools.
        """

        self._tools.clear()