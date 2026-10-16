from app.agents.composer.prompt_composer import PromptComposer
from app.agents.runtime.builder import RuntimeBuilder
from app.agents.tools.registry import ToolRegistry

from tests.fixtures.llm import DummyLLMProvider


def test_runtime_builder_creates_context():
    provider = DummyLLMProvider()

    context = RuntimeBuilder.build(provider)

    assert context.llm_provider is provider
    assert isinstance(context.prompt_composer, PromptComposer)
    assert isinstance(context.tool_registry, ToolRegistry)