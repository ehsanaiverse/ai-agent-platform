from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolCall(BaseModel):
    """
    Represents a request to execute a tool.
    """

    model_config = ConfigDict(frozen=True)

    tool_name: str = Field(
        ...,
        description="Unique name of the tool to execute.",
    )

    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to the tool.",
    )


class ToolResult(BaseModel):
    """
    Standardized response returned by every tool.
    """

    model_config = ConfigDict(frozen=True)

    success: bool = Field(
        ...,
        description="Whether the tool executed successfully.",
    )

    output: Any | None = Field(
        default=None,
        description="Output produced by the tool.",
    )

    error: str | None = Field(
        default=None,
        description="Error message when execution fails.",
    )