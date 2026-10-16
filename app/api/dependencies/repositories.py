from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db_session

from app.repositories.user_repository import UserRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository


def get_user_repository(
    db: Session = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(db)


def get_conversation_repository(
    db: Session = Depends(get_db_session),
) -> ConversationRepository:
    return ConversationRepository(db)


def get_message_repository(
    db: Session = Depends(get_db_session),
) -> MessageRepository:
    return MessageRepository(db)