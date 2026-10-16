import json
import traceback
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response
import structlog

from app.api.dependencies.channels import get_channel_service, get_whatsapp_adapter
from app.channels.whatsapp.adapter import WhatsAppAdapter
from app.core.config import settings
from app.core.security import verify_whatsapp_signature
from app.services.channel_service import ChannelService

logger = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/channels/whatsapp/webhook",
    tags=["WhatsApp Webhook"],
)


@router.get("", response_class=Response)
@router.get("/", response_class=Response, include_in_schema=False)
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """
    Handle Meta WhatsApp Webhook verification challenge (GET request).
    
    Meta sends hub.mode, hub.verify_token, and hub.challenge. If verify_token matches,
    return hub.challenge as plain text.
    """
    logger.info("Received WhatsApp webhook verification request", mode=hub_mode)

    expected_verify_token = settings.VERIFY_TOKEN or settings.WEBHOOK_VERIFY_TOKEN

    if hub_mode == "subscribe" and hub_verify_token and hub_verify_token == expected_verify_token:
        logger.info("WhatsApp webhook verified successfully")
        return Response(content=hub_challenge or "", media_type="text/plain", status_code=200)

    logger.warning("WhatsApp webhook verification failed: Token mismatch or invalid mode")
    raise HTTPException(status_code=403, detail="Webhook verification failed: Invalid verify token or mode")


@router.post("")
@router.post("/", include_in_schema=False)
async def handle_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    whatsapp_adapter: WhatsAppAdapter = Depends(get_whatsapp_adapter),
    channel_service: ChannelService = Depends(get_channel_service),
):
    """
    Handle incoming WhatsApp Webhook events (POST request).
    
    Validates X-Hub-Signature-256 if WHATSAPP_APP_SECRET is configured, parses payload,
    normalizes messages, and delegates execution to ChannelService.
    """
    body_bytes = await request.body()

    # Enforce signature verification if APP_SECRET is configured
    if settings.WHATSAPP_APP_SECRET:
        is_valid_sig = verify_whatsapp_signature(
            payload=body_bytes,
            signature_header=x_hub_signature_256,
            app_secret=settings.WHATSAPP_APP_SECRET,
        )
        if not is_valid_sig:
            logger.warning("Rejecting WhatsApp webhook with invalid HMAC signature")
            raise HTTPException(status_code=401, detail="Invalid request signature")

    try:
        raw_payload = json.loads(body_bytes.decode("utf-8"))
    except Exception as exc:
        logger.error("Malformed JSON in WhatsApp webhook request", error=str(exc))
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    logger.info("Received WhatsApp webhook payload", payload_object=raw_payload.get("object"))

    # Normalize vendor payload to channel-agnostic domain models
    normalized_messages = whatsapp_adapter.normalize_incoming(raw_payload)

    # Process normalized messages through ChannelService -> AgentService
    failed_messages = []
    for incoming_msg in normalized_messages:
        try:
            await channel_service.process_incoming_message(incoming_msg)
        except Exception as exc:
            logger.error(
                "Error processing incoming WhatsApp message",
                message_id=incoming_msg.message_id,
                error=str(exc),
                traceback=traceback.format_exc(),
            )
            failed_messages.append(incoming_msg.message_id)

    return {
        "status": "success",
        "processed_messages": len(normalized_messages),
        "failed_messages": failed_messages,
    }
