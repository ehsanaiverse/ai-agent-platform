from fastapi import Depends

from app.agents.runner import AgentRunner
from app.api.dependencies.llm import get_llm_provider
from app.llm.providers.base import BaseLLMProvider


def get_agent_runner(
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
) -> AgentRunner:
    return AgentRunner(
    llm_provider=llm_provider,
)