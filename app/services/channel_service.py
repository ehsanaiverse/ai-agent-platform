from typing import Optional
import structlog

from app.api.schemas.chat import ChatRequest
from app.channels.schemas import ChannelType, IncomingChannelMessage, OutgoingChannelMessage
from app.channels.whatsapp.client import WhatsAppClient
from app.services.agent_service import AgentService

logger = structlog.get_logger(__name__)


class ChannelService:
    """
    Channel orchestration service.

    Coordinates provider-independent incoming channel messages with the AI core (AgentService),
    and dispatches agent responses back to the recipient via channel clients.
    """

    def __init__(
        self,
        agent_service: AgentService,
        whatsapp_client: WhatsAppClient,
    ):
        self.agent_service = agent_service
        self.whatsapp_client = whatsapp_client

    async def process_incoming_message(
        self,
        message: IncomingChannelMessage,
    ) -> Optional[OutgoingChannelMessage]:
        """
        Process a single normalized incoming channel message through the AI platform pipeline.

        Args:
            message: Provider-independent incoming message model.

        Returns:
            Optional[OutgoingChannelMessage]: Response message dispatched to recipient.
        """
        logger.info(
            "Processing incoming channel message",
            channel=message.channel.value,
            sender_id=message.sender_id,
            message_id=message.message_id,
        )

        chat_request = ChatRequest(
            platform=message.channel.value,
            platform_user_id=message.sender_id,
            display_name=message.display_name,
            message=message.text,
        )

        logger.info("Calling AgentService")
        
        # Call AI core (AgentService)
        chat_response = await self.agent_service.chat(chat_request)
        
        logger.info(
            "AgentService returned",
            response=chat_response.response,
        )
        
        outgoing_msg = OutgoingChannelMessage(
            recipient_id=message.sender_id,
            text=chat_response.response,
            reply_to_message_id=message.message_id,
        )
        
        logger.info(
            "Sending WhatsApp reply",
            recipient=outgoing_msg.recipient_id,
        )

        # Dispatch according to channel
        if message.channel == ChannelType.WHATSAPP:
            await self.whatsapp_client.send_text_message(
                recipient_id=outgoing_msg.recipient_id,
                text=outgoing_msg.text,
                reply_to_message_id=outgoing_msg.reply_to_message_id,
            )
            # Mark incoming message as read asynchronously
            await self.whatsapp_client.mark_message_as_read(message.message_id)

        logger.info("WhatsApp send completed")

        logger.info(
            "Successfully processed and delivered channel response",
            channel=message.channel.value,
            recipient_id=outgoing_msg.recipient_id,
        )

        return outgoing_msg
