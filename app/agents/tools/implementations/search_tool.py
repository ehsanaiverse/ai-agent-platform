"""
Web Search tool implementation.

Performs web search queries to fetch external search results.
"""

from __future__ import annotations

import json
from typing import Any
import httpx

from app.agents.tools.base import BaseTool
from app.agents.tools.metadata import ToolMetadata
from app.agents.tools.parameters import ToolParameter, ToolParameterType
from app.agents.tools.schemas import ToolCall, ToolResult


class SearchTool(BaseTool):
    """
    Tool for performing web searches.
    """

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Searches the web for up-to-date information given a query."

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=[
                ToolParameter(
                    name="query",
                    type=ToolParameterType.STRING,
                    description="Search query string.",
                    required=True,
                ),
            ],
        )

    async def execute(self, call: ToolCall) -> ToolResult:
        query = call.arguments.get("query")
        if not query:
            return ToolResult(
                success=False,
                output="",
                error="Missing required argument 'query'.",
            )

        try:
            # Uses DuckDuckGo instant answer / HTML endpoint for lightweight web search
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1",
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    abstract = data.get("AbstractText") or data.get("Heading") or ""
                    related_topics = [
                        topic.get("Text")
                        for topic in data.get("RelatedTopics", [])
                        if isinstance(topic, dict) and "Text" in topic
                    ][:3]

                    result_payload = {
                        "query": query,
                        "summary": abstract or "No direct abstract summary found.",
                        "results": related_topics,
                    }
                    return ToolResult(
                        success=True,
                        output=json.dumps(result_payload),
                    )

            return ToolResult(
                success=True,
                output=f"Search performed for query: {query}",
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                output="",
                error=f"Web search failed: {exc}",
            )
