import pytest

from app.agents.tools.base import BaseTool
from app.agents.tools.exceptions import (
    DuplicateToolRegistrationError,
    ToolNotFoundError,
)
from app.agents.tools.registry import ToolRegistry
from app.agents.tools.schemas import ToolCall, ToolResult


class DummyTool(BaseTool):
    @property
    def name(self) -> str:
        return "dummy"

    @property
    def description(self) -> str:
        return "Dummy tool used for testing."

    async def execute(self, call: ToolCall) -> ToolResult:
        return ToolResult(
            success=True,
            output="OK",
        )


@pytest.fixture
def registry() -> ToolRegistry:
    return ToolRegistry()


@pytest.fixture
def dummy_tool() -> DummyTool:
    return DummyTool()


def test_register_tool(registry: ToolRegistry, dummy_tool: DummyTool) -> None:
    registry.register(dummy_tool)

    assert registry.has("dummy")


def test_get_registered_tool(
    registry: ToolRegistry,
    dummy_tool: DummyTool,
) -> None:
    registry.register(dummy_tool)

    tool = registry.get("dummy")

    assert tool is dummy_tool


def test_duplicate_registration_raises_error(
    registry: ToolRegistry,
    dummy_tool: DummyTool,
) -> None:
    registry.register(dummy_tool)

    with pytest.raises(DuplicateToolRegistrationError):
        registry.register(dummy_tool)


def test_get_unknown_tool_raises_error(
    registry: ToolRegistry,
) -> None:
    with pytest.raises(ToolNotFoundError):
        registry.get("calculator")


def test_list_tools_returns_sorted_names(
    registry: ToolRegistry,
    dummy_tool: DummyTool,
) -> None:
    registry.register(dummy_tool)

    assert registry.list_tools() == ["dummy"]


def test_unregister_tool(
    registry: ToolRegistry,
    dummy_tool: DummyTool,
) -> None:
    registry.register(dummy_tool)

    registry.unregister("dummy")

    assert not registry.has("dummy")


def test_clear_registry(
    registry: ToolRegistry,
    dummy_tool: DummyTool,
) -> None:
    registry.register(dummy_tool)

    registry.clear()

    assert registry.list_tools() == []


def test_get_metadata(
    registry: ToolRegistry,
    dummy_tool: DummyTool,
) -> None:
    registry.register(dummy_tool)

    metadata = registry.get_metadata("dummy")

    assert metadata.name == "dummy"
    assert metadata.description == "Dummy tool used for testing."


def test_list_metadata(
    registry: ToolRegistry,
    dummy_tool: DummyTool,
) -> None:
    registry.register(dummy_tool)

    metadata_list = registry.list_metadata()

    assert len(metadata_list) == 1
    assert metadata_list[0].name == "dummy"