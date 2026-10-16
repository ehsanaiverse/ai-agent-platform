import pytest

from app.agents.tools.implementations.calculator import CalculatorTool
from app.agents.tools.implementations.datetime_tool import DateTimeTool
from app.agents.tools.implementations.http_tool import HTTPTool
from app.agents.tools.implementations.search_tool import SearchTool
from app.agents.tools.schemas import ToolCall


@pytest.mark.asyncio
async def test_calculator_tool_success() -> None:
    tool = CalculatorTool()
    call = ToolCall(tool_name="calculator", arguments={"expression": "100 / (2 + 3) * 4"})
    result = await tool.execute(call)

    assert result.success is True
    assert result.output == "80.0"


@pytest.mark.asyncio
async def test_calculator_tool_invalid_expression() -> None:
    tool = CalculatorTool()
    call = ToolCall(tool_name="calculator", arguments={"expression": "import os; os.system('echo test')"})
    result = await tool.execute(call)

    assert result.success is False
    assert "Calculation error" in result.error or "Invalid arithmetic expression" in result.error


@pytest.mark.asyncio
async def test_datetime_tool_utc() -> None:
    tool = DateTimeTool()
    call = ToolCall(tool_name="datetime", arguments={"timezone": "UTC"})
    result = await tool.execute(call)

    assert result.success is True
    assert "UTC" in result.output
    assert "iso" in result.output


@pytest.mark.asyncio
async def test_http_tool_mock() -> None:
    tool = HTTPTool()
    call = ToolCall(tool_name="http_client", arguments={"url": "https://httpbin.org/get", "method": "GET"})
    result = await tool.execute(call)

    assert isinstance(result.success, bool)


@pytest.mark.asyncio
async def test_search_tool_execution() -> None:
    tool = SearchTool()
    call = ToolCall(tool_name="web_search", arguments={"query": "AI Agent Platform"})
    result = await tool.execute(call)

    assert result.success is True
    assert "query" in result.output
