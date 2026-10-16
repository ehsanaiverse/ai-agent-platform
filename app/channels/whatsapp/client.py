from typing import Any, Dict, Optional
import httpx
import structlog

logger = structlog.get_logger(__name__)


class WhatsAppClientError(Exception):
    """Custom exception raised when Meta WhatsApp Cloud API calls fail."""
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class WhatsAppClient:
    """
    Dedicated client for Meta WhatsApp Cloud API operations.
    
    Handles HTTP request formatting, authorization headers, timeout safety,
    exception handling, and non-sensitive logging.
    """

    def __init__(
        self,
        access_token: str,
        phone_number_id: str,
        api_version: str = "v21.0",
        base_url: str = "https://graph.facebook.com",
        timeout: float = 15.0,
    ):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.api_version = api_version
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def _messages_url(self) -> str:
        return f"{self.base_url}/{self.api_version}/{self.phone_number_id}/messages"

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def send_text_message(
        self,
        recipient_id: str,
        text: str,
        reply_to_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a plain text message to a WhatsApp recipient.

        Args:
            recipient_id: Target WhatsApp phone number (e.g. '15551234567').
            text: Text body content.
            reply_to_message_id: Optional incoming message ID for contextual reply.

        Returns:
            Dict response from Meta API.

        Raises:
            WhatsAppClientError: On network, timeout, or Meta API errors.
        """
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text,
            },
        }

        if reply_to_message_id:
            payload["context"] = {"message_id": reply_to_message_id}

        return await self._post(self._messages_url, payload)

    async def mark_message_as_read(self, message_id: str) -> bool:
        """
        Mark an incoming WhatsApp message as read.

        Args:
            message_id: Meta WhatsApp message ID.

        Returns:
            bool: True if status updated successfully.
        """
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        try:
            await self._post(self._messages_url, payload)
            return True
        except WhatsAppClientError as exc:
            logger.warning(
                "Failed to mark WhatsApp message as read",
                message_id=message_id,
                error=str(exc),
            )
            return False

    async def _post(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper for executing POST requests safely."""
        if not self.access_token or not self.phone_number_id:
            logger.error("WhatsApp credentials missing from client config")
            raise WhatsAppClientError(
                "WhatsApp client is unconfigured (missing WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID)"
            )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._headers,
                )

                if response.status_code >= 400:
                    try:
                        error_json = response.json()
                    except Exception:
                        error_json = {"raw": response.text}

                    logger.error(
                        "WhatsApp API request failed",
                        status_code=response.status_code,
                    )
                    raise WhatsAppClientError(
                        f"Meta WhatsApp API error ({response.status_code}): {error_json}",
                        status_code=response.status_code,
                        response_data=error_json,
                    )

                logger.info(
                    "WhatsApp API request succeeded",
                    status_code=response.status_code,
                )
                return response.json()

            except httpx.TimeoutException as exc:
                logger.error("WhatsApp API request timed out")
                raise WhatsAppClientError(f"WhatsApp API request timed out: {exc}") from exc
            except httpx.RequestError as exc:
                logger.error("WhatsApp API network error", error=str(exc))
                raise WhatsAppClientError(f"WhatsApp API network error: {exc}") from exc
