from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.channels.schemas import IncomingChannelMessage, OutgoingChannelMessage


class BaseChannelAdapter(ABC):
    """
    Abstract Base Class for communication channel adapters.
    
    Responsibilities:
    1. Convert vendor-specific incoming webhook JSON into normalized IncomingChannelMessage instances.
    2. Convert platform OutgoingChannelMessage instances into vendor-specific API request JSON payloads.
    
    This isolates vendor JSON structures completely from core business services and LLM agents.
    """

    @abstractmethod
    def normalize_incoming(self, raw_payload: Dict[str, Any]) -> List[IncomingChannelMessage]:
        """
        Parse and normalize vendor-specific JSON payload into standard IncomingChannelMessage list.

        Args:
            raw_payload: Raw JSON dictionary received from the channel's webhook.

        Returns:
            List of normalized IncomingChannelMessage instances. Returns empty list if payload
            contains unsupported event types or non-message notifications.
        """
        pass

    @abstractmethod
    def denormalize_outgoing(self, message: OutgoingChannelMessage) -> Dict[str, Any]:
        """
        Convert standard OutgoingChannelMessage into vendor-specific API JSON payload.

        Args:
            message: Standardized outgoing channel message.

        Returns:
            Dict containing formatted vendor API payload.
        """
        pass
