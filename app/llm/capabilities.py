"""
LLM capability models.

These models describe what features an LLM provider supports.
"""

from pydantic import BaseModel, ConfigDict, Field


class LLMCapabilities(BaseModel):
    """
    Describes the capabilities supported by an LLM provider.
    """

    model_config = ConfigDict(frozen=True)

    streaming: bool = Field(default=False)
    tool_calling: bool = Field(default=False)
    structured_output: bool = Field(default=False)
    vision: bool = Field(default=False)