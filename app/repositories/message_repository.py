from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """
    Repository responsible for Message persistence.
    """

    def __init__(self, db: Session):
        super().__init__(db, Message)

    def get_by_conversation_id(self, conversation_id):
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )

        return self.db.scalars(stmt).all()
    
    
    def get_recent_by_conversation_id(
        self,
        conversation_id: UUID,
        limit: int,
    ) -> list[Message]:
        """
        Return the most recent messages in chronological order.
        """

        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        messages = self.db.scalars(stmt).all()

        return list(reversed(messages))