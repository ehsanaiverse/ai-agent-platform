"""
Groq AI Tool Calling Adapter.

Formats ToolMetadata into Groq-compatible tool calling schemas and parses
Groq API response objects or dictionary payloads into standardized ToolCall instances.
"""

from __future__ import annotations

import json
from typing import Any

from app.agents.tools.adapters.base import BaseToolAdapter
from app.agents.tools.metadata import ToolMetadata
from app.agents.tools.schemas import ToolCall


class GroqToolAdapter(BaseToolAdapter):
    """
    Adapter for Groq AI function calling & tool use specification.
    """

    def format_tools(self, tools: list[ToolMetadata]) -> list[dict[str, Any]]:
        """
        Format a list of ToolMetadata into Groq function calling tool specifications.
        """
        formatted = []
        for tool in tools:
            properties = {}
            required = []

            for param in tool.parameters:
                properties[param.name] = {
                    "type": param.type.value,
                    "description": param.description,
                }
                if param.required:
                    required.append(param.name)

            formatted.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            })
        return formatted

    def parse_tool_call(self, response: Any) -> ToolCall | None:
        """
        Parse raw Groq response dictionary, message object, or tool call dict into a ToolCall.
        """
        if not response:
            return None

        # Case 1: Direct ToolCall instance
        if isinstance(response, ToolCall):
            return response

        # Case 2: Dictionary payload
        if isinstance(response, dict):
            if "function" in response:
                func_data = response["function"]
                name = func_data.get("name")
                args = func_data.get("arguments", {})
            else:
                name = response.get("name") or response.get("tool_name")
                args = response.get("arguments", {})

            if not name:
                return None

            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}

            return ToolCall(tool_name=name, arguments=args)

        # Case 3: Response object with tool_calls attribute (e.g. ChatGroq AIMessage)
        tool_calls = getattr(response, "tool_calls", None)
        if tool_calls and len(tool_calls) > 0:
            first_call = tool_calls[0]
            if isinstance(first_call, dict):
                name = first_call.get("name") or first_call.get("function", {}).get("name")
                args = first_call.get("args") or first_call.get("arguments", {})
            else:
                name = getattr(first_call, "name", None) or getattr(getattr(first_call, "function", None), "name", None)
                args = getattr(first_call, "args", None) or getattr(getattr(first_call, "function", None), "arguments", {})

            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}

            if name:
                return ToolCall(tool_name=name, arguments=args or {})

        return None
