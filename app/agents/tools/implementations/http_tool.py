"""
HTTP Client tool implementation.

Executes external HTTP requests (GET, POST, PUT, DELETE) using httpx.
"""

from __future__ import annotations

import json
from typing import Any
import httpx

from app.agents.tools.base import BaseTool
from app.agents.tools.metadata import ToolMetadata
from app.agents.tools.parameters import ToolParameter, ToolParameterType
from app.agents.tools.schemas import ToolCall, ToolResult


class HTTPTool(BaseTool):
    """
    Tool for calling external HTTP APIs.
    """

    @property
    def name(self) -> str:
        return "http_client"

    @property
    def description(self) -> str:
        return "Makes external HTTP requests (GET, POST, PUT, DELETE)."

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=[
                ToolParameter(
                    name="url",
                    type=ToolParameterType.STRING,
                    description="Target HTTP/HTTPS URL.",
                    required=True,
                ),
                ToolParameter(
                    name="method",
                    type=ToolParameterType.STRING,
                    description="HTTP method: GET, POST, PUT, DELETE. Defaults to GET.",
                    required=False,
                ),
                ToolParameter(
                    name="headers",
                    type=ToolParameterType.OBJECT,
                    description="Optional HTTP headers as key-value pairs.",
                    required=False,
                ),
                ToolParameter(
                    name="params",
                    type=ToolParameterType.OBJECT,
                    description="Optional URL query parameters as key-value pairs.",
                    required=False,
                ),
                ToolParameter(
                    name="body",
                    type=ToolParameterType.OBJECT,
                    description="Optional JSON payload body as key-value pairs.",
                    required=False,
                ),
            ],
        )

    async def execute(self, call: ToolCall) -> ToolResult:
        url = call.arguments.get("url")
        if not url:
            return ToolResult(
                success=False,
                output="",
                error="Missing required argument 'url'.",
            )

        method = str(call.arguments.get("method", "GET")).upper()
        headers = call.arguments.get("headers") or {}
        params = call.arguments.get("params") or {}
        body = call.arguments.get("body")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=body if body else None,
                )

                try:
                    content = response.json()
                except Exception:
                    content = response.text

                output_payload = {
                    "status_code": response.status_code,
                    "content": content,
                }

                return ToolResult(
                    success=response.is_success,
                    output=json.dumps(output_payload) if isinstance(content, (dict, list)) else str(output_payload),
                )
        except Exception as exc:
            return ToolResult(
                success=False,
                output="",
                error=f"HTTP Request failed: {exc}",
            )
