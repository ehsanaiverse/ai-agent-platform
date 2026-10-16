from app.agents.tools.base import BaseTool
from app.agents.tools.schemas import ToolCall, ToolResult


class DummyTool(BaseTool):

    @property
    def name(self) -> str:
        return "dummy"

    async def execute(self, call: ToolCall) -> ToolResult:
        return ToolResult(
            success=True,
            output="OK",
        )

tool = DummyTool()

print(tool.name)
print(tool.description)