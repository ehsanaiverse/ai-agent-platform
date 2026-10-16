"""
Tool parameter models.

These models describe the input parameters accepted by a tool.
They are independent of any LLM provider and can later be mapped
to OpenAI, Anthropic, Groq, Gemini, or any future provider.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ToolParameterType(str, Enum):
    """
    Supported parameter types.
    """

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class ToolParameter(BaseModel):
    """
    Describes a single input parameter accepted by a tool.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(
        ...,
        description="Unique parameter name.",
    )

    type: ToolParameterType = Field(
        ...,
        description="Parameter data type.",
    )

    description: str = Field(
        ...,
        description="Human-readable description.",
    )

    required: bool = Field(
        default=True,
        description="Whether this parameter is required.",
    )