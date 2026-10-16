from fastapi import Depends

from app.api.dependencies.services import get_agent_service
from app.channels.whatsapp.adapter import WhatsAppAdapter
from app.channels.whatsapp.client import WhatsAppClient
from app.core.config import settings
from app.services.agent_service import AgentService
from app.services.channel_service import ChannelService


def get_whatsapp_client() -> WhatsAppClient:
    """Dependency provider for WhatsAppClient."""
    return WhatsAppClient(
        access_token=settings.WHATSAPP_ACCESS_TOKEN,
        phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID,
        api_version=settings.WHATSAPP_API_VERSION,
        base_url=settings.WHATSAPP_BASE_URL,
    )


def get_whatsapp_adapter() -> WhatsAppAdapter:
    """Dependency provider for WhatsAppAdapter."""
    return WhatsAppAdapter()


def get_channel_service(
    agent_service: AgentService = Depends(get_agent_service),
    whatsapp_client: WhatsAppClient = Depends(get_whatsapp_client),
) -> ChannelService:
    """Dependency provider for ChannelService."""
    return ChannelService(
        agent_service=agent_service,
        whatsapp_client=whatsapp_client,
    )
