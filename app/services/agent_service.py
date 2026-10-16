# from app.services.user_service import UserService
# from app.services.conversation_service import ConversationService
# from app.services.message_service import MessageService
# from app.agents.runner import AgentRunner
# from app.agents.state.conversation_state import ConversationState
# from app.api.schemas.chat import ChatRequest, ChatResponse
# from app.llm.schemas import LLMMessage, MessageRole


# class AgentService:
#     def __init__(
#         self,
#         user_service: UserService,
#         conversation_service: ConversationService,
#         message_service: MessageService,
#         agent_runner: AgentRunner,
#     ):
#         self.user_service = user_service
#         self.conversation_service = conversation_service
#         self.message_service = message_service
#         self.agent_runner = agent_runner

#     async def chat(self, request: ChatRequest) -> ChatResponse:
#         user = self.user_service.get_or_create_user(
#             platform=request.platform,
#             platform_user_id=request.platform_user_id,
#             display_name=request.display_name,
#         )

#         conversation = self.conversation_service.create_conversation(
#             user_id=user.id,
#         )

#         self.message_service.save_message(
#             conversation_id=conversation.id,
#             role=MessageRole.USER,
#             content=request.message,
#         )

#         state: ConversationState = {
#             "conversation_id": str(conversation.id),
#             "user_id": str(user.id),
#             "messages": [
#                 LLMMessage(role=MessageRole.USER, content=request.message),
#             ],
#         }

#         result = await self.agent_runner.run(state)

#         self.message_service.save_message(
#             conversation_id=conversation.id,
#             role=MessageRole.ASSISTANT,
#             content=result["response"],
#         )

#         return ChatResponse(
#             conversation_id=str(conversation.id),
#             response=result["response"],
#         )



from sqlalchemy.orm import Session

from app.agents.runner import AgentRunner
from app.agents.state.conversation_state import ConversationState

from app.api.schemas.chat import ChatRequest, ChatResponse

from app.llm.schemas import LLMMessage, MessageRole

from app.services.user_service import UserService
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService


class AgentService:
    """
    Application service responsible for orchestrating the
    complete AI request workflow.

    This service owns the transaction boundary.
    """

    def __init__(
        self,
        db: Session,
        user_service: UserService,
        conversation_service: ConversationService,
        message_service: MessageService,
        agent_runner: AgentRunner,
    ):
        self.db = db
        self.user_service = user_service
        self.conversation_service = conversation_service
        self.message_service = message_service
        self.agent_runner = agent_runner

    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Execute the complete AI chat workflow.

        Workflow

        1. Find or create user
        2. Create conversation
        3. Persist user message
        4. Build conversation state
        5. Execute LangGraph
        6. Persist assistant response
        7. Commit transaction
        """

        try:
            user = self.user_service.get_or_create_user(
                platform=request.platform,
                platform_user_id=request.platform_user_id,
                display_name=request.display_name,
            )

            conversation = (
                self.conversation_service.get_or_create_conversation(
                    user_id=user.id,
                )
            )

            self.message_service.save_message(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=request.message,
            )

            llm_messages = self.message_service.build_llm_messages(
                conversation.id
            )

            state: ConversationState = {
                "conversation_id": str(conversation.id),
                "user_id": str(user.id),
                "messages": llm_messages,
                "latest_message": request.message,
            }

            agent_result = await self.agent_runner.run(state)

            self.message_service.save_message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=agent_result["response"],
            )

            self.db.commit()

            return ChatResponse(
                conversation_id=str(conversation.id),
                response=agent_result["response"],
            )

        except Exception:
            self.db.rollback()
            raise