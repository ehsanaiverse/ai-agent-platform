from typing import Any, Dict, List
import structlog

from app.channels.base import BaseChannelAdapter
from app.channels.schemas import (
    ChannelType,
    IncomingChannelMessage,
    MessageType,
    OutgoingChannelMessage,
)
from app.channels.whatsapp.schemas import WhatsAppWebhookPayload

logger = structlog.get_logger(__name__)


class WhatsAppAdapter(BaseChannelAdapter):
    """
    Adapter implementation for Meta WhatsApp Cloud API.
    
    Converts raw Meta webhook JSON structures into normalized IncomingChannelMessage domain models,
    and converts OutgoingChannelMessage domain models into Meta API request payloads.
    """

    def normalize_incoming(
        self,
        raw_payload: Dict[str, Any],
    ) -> List[IncomingChannelMessage]:
        """
        Parse and normalize vendor-specific WhatsApp webhook JSON into standard IncomingChannelMessage model(s).

        Args:
            raw_payload: Raw JSON dictionary received from Meta webhook.

        Returns:
            List of normalized IncomingChannelMessage instances.
        """
        try:
            payload = WhatsAppWebhookPayload.model_validate(raw_payload)
        except Exception as exc:
            logger.warning("Failed to parse WhatsApp webhook payload", error=str(exc))
            return []

        normalized_messages: List[IncomingChannelMessage] = []

        for entry in payload.entry:
            for change in entry.changes:
                value = change.value
                if not value.messages:
                    continue

                # Build contact mapping for sender display names
                contact_names: Dict[str, str] = {}
                if value.contacts:
                    for contact in value.contacts:
                        if contact.wa_id and contact.profile and contact.profile.name:
                            contact_names[contact.wa_id] = contact.profile.name

                for message in value.messages:
                    # Phase 1 scope: process text messages only
                    if message.type != "text" or not message.text or not message.text.body:
                        logger.info(
                            "Ignoring non-text or empty WhatsApp message",
                            message_id=message.id,
                            message_type=message.type,
                        )
                        continue

                    display_name = contact_names.get(message.from_user, "WhatsApp User")
                    timestamp_int = int(message.timestamp) if message.timestamp and message.timestamp.isdigit() else None

                    incoming_msg = IncomingChannelMessage(
                        channel=ChannelType.WHATSAPP,
                        sender_id=message.from_user,
                        display_name=display_name,
                        message_id=message.id,
                        message_type=MessageType.TEXT,
                        text=message.text.body,
                        timestamp=timestamp_int,
                        metadata={
                            "wa_id": message.from_user,
                            "field": change.field,
                        },
                    )
                    normalized_messages.append(incoming_msg)

        return normalized_messages

    def denormalize_outgoing(
        self,
        message: OutgoingChannelMessage,
    ) -> Dict[str, Any]:
        """
        Convert standard OutgoingChannelMessage into Meta WhatsApp API payload format.

        Args:
            message: Standardized outgoing channel message.

        Returns:
            Dict representing Meta API request payload.
        """
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": message.recipient_id,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message.text,
            },
        }

        if message.reply_to_message_id:
            payload["context"] = {"message_id": message.reply_to_message_id}

        return payload
