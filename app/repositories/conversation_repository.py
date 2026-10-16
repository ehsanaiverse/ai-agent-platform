from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """
    Repository responsible for Conversation persistence.
    """

    def __init__(self, db: Session):
        super().__init__(db, Conversation)

    def get_by_user_id(self, user_id):
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )

        return self.db.scalars(stmt).all()
    
    def get_latest_by_user_id(
        self,
        user_id: UUID,
    ) -> Conversation | None:
        """
        Return the most recent conversation for a user.
        """

        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(1)
        )

        return self.db.scalar(stmt)