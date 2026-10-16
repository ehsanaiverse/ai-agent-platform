from uuid import UUID

from app.database.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository


class ConversationService:
    """
    Business logic related to conversations.
    """

    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def create_conversation(
        self,
        user_id: UUID,
        title: str = "New Conversation",
    ) -> Conversation:
        """
        Create a new conversation for a user.
        """

        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.repository.add(conversation)
        self.repository.flush()
        self.repository.refresh(conversation)

        return conversation

    def get_user_conversations(
        self,
        user_id: UUID,
    ) -> list[Conversation]:
        """
        Return all conversations for a user.
        """

        return self.repository.get_by_user_id(user_id)
    
    
    def get_or_create_conversation(
        self,
        user_id: UUID,
    ) -> Conversation:
        """
        Return the latest conversation for the user.
        Create one if none exists.
        """

        conversation = self.repository.get_latest_by_user_id(
            user_id
        )

        if conversation:
            return conversation

        return self.create_conversation(
            user_id=user_id,
        )