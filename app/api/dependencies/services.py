from fastapi import Depends

from app.agents.runner import AgentRunner
from app.repositories.user_repository import UserRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository

from app.services.user_service import UserService
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService


from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db_session
from app.services.agent_service import AgentService

from app.api.dependencies.repositories import (
    get_user_repository,
    get_conversation_repository,
    get_message_repository,
)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository)


def get_conversation_service(
    repository: ConversationRepository = Depends(
        get_conversation_repository
    ),
) -> ConversationService:
    return ConversationService(repository)


def get_message_service(
    repository: MessageRepository = Depends(get_message_repository),
) -> MessageService:
    return MessageService(repository)


from app.api.dependencies.agent import get_agent_runner


# def get_agent_service(
#     user_service: UserService = Depends(get_user_service),
#     conversation_service: ConversationService = Depends(
#         get_conversation_service
#     ),
#     message_service: MessageService = Depends(
#         get_message_service
#     ),
#     agent_runner: AgentRunner = Depends(get_agent_runner),
# ) -> AgentService:
#     return AgentService(
#         user_service=user_service,
#         conversation_service=conversation_service,
#         message_service=message_service,
#         agent_runner=agent_runner,
#     )

def get_agent_service(
    db: Session = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
    conversation_service: ConversationService = Depends(
        get_conversation_service
    ),
    message_service: MessageService = Depends(
        get_message_service
    ),
    agent_runner: AgentRunner = Depends(get_agent_runner),
) -> AgentService:
    return AgentService(
        db=db,
        user_service=user_service,
        conversation_service=conversation_service,
        message_service=message_service,
        agent_runner=agent_runner,
    )