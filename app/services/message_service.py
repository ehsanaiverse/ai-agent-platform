from uuid import UUID

from app.database.models.message import Message
from app.repositories.message_repository import MessageRepository
from app.llm.schemas import LLMMessage
from app.core.config import settings

class MessageService:
    """
    Business logic related to messages.
    """

    def __init__(self, repository: MessageRepository):
        self.repository = repository

    def save_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
    ) -> Message:
        """
        Save a message to a conversation.
        """

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        self.repository.add(message)
        self.repository.flush()
        self.repository.refresh(message)

        return message

    def get_conversation_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        """
        Return all messages for a conversation.
        """

        return self.repository.get_by_conversation_id(
            conversation_id
        )
    
    
    def build_llm_messages(
        self,
        conversation_id: UUID,
    ) -> list[LLMMessage]:
        """
        Build the conversation window sent to the LLM.
        """

        messages = self.repository.get_recent_by_conversation_id(
            conversation_id=conversation_id,
            limit=settings.MEMORY_WINDOW_SIZE,
        )

        return [
            LLMMessage(
                role=message.role,
                content=message.content,
            )
            for message in messages
        ]