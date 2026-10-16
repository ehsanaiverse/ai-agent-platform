from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from app.api.dependencies.services import get_agent_service
from app.api.schemas.chat import ChatRequest
from app.api.schemas.chat import ChatResponse
from app.services.agent_service import AgentService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message to the AI agent",
    description=(
        "Temporary endpoint used to verify the complete "
        "AI request pipeline before communication "
        "channel integrations."
    ),
)
async def chat(
    request: ChatRequest,
    service: AgentService = Depends(get_agent_service),
) -> ChatResponse:
    """
    Delegate the request to the application service.

    The API layer intentionally contains no business logic.
    """

    return await service.chat(request)