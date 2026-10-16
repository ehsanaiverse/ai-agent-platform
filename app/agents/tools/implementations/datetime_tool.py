"""
DateTime tool implementation.

Provides current date, time, and timezone information.
"""

from __future__ import annotations

from datetime import datetime, timezone
import zoneinfo

from app.agents.tools.base import BaseTool
from app.agents.tools.metadata import ToolMetadata
from app.agents.tools.parameters import ToolParameter, ToolParameterType
from app.agents.tools.schemas import ToolCall, ToolResult


class DateTimeTool(BaseTool):
    """
    Tool for fetching current date and time in specified timezone.
    """

    @property
    def name(self) -> str:
        return "datetime"

    @property
    def description(self) -> str:
        return "Returns current date, time, and timezone information."

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=[
                ToolParameter(
                    name="timezone",
                    type=ToolParameterType.STRING,
                    description="Target timezone name (e.g., 'UTC', 'America/New_York', 'Asia/Karachi'). Defaults to UTC.",
                    required=False,
                ),
            ],
        )

    async def execute(self, call: ToolCall) -> ToolResult:
        tz_name = call.arguments.get("timezone", "UTC") or "UTC"

        try:
            if tz_name.upper() == "UTC":
                tz = timezone.utc
            else:
                tz = zoneinfo.ZoneInfo(tz_name)

            now = datetime.now(tz)
            output_data = {
                "iso": now.isoformat(),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "timezone": str(tz),
                "day_of_week": now.strftime("%A"),
            }

            return ToolResult(
                success=True,
                output=str(output_data),
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                output="",
                error=f"Invalid timezone or datetime error: {exc}",
            )
