"""
Tool metadata models.

Every tool exposes a standardized description that can be consumed
by any LLM provider capable of tool/function calling.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.agents.tools.parameters import ToolParameter


class ToolMetadata(BaseModel):
    """
    Standardized description of a tool.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(
        ...,
        description="Unique tool name.",
    )

    description: str = Field(
        ...,
        description="Human-readable description of the tool.",
    )

    parameters: list[ToolParameter] = Field(
        default_factory=list,
        description="Input parameters accepted by the tool.",
    )