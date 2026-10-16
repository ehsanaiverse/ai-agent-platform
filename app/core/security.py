import hmac
import hashlib
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


def verify_whatsapp_signature(
    payload: bytes,
    signature_header: Optional[str],
    app_secret: str,
) -> bool:
    """
    Verify the X-Hub-Signature-256 header sent by Meta WhatsApp webhook using HMAC SHA-256.

    Args:
        payload: Raw HTTP request body bytes.
        signature_header: Value of the 'X-Hub-Signature-256' header (e.g., 'sha256=...').
        app_secret: Meta Application Secret key from configuration.

    Returns:
        bool: True if signature matches, False otherwise.
    """
    if not app_secret:
        logger.warning("WhatsApp app secret is not configured in settings")
        return False

    if not signature_header:
        logger.warning("Missing X-Hub-Signature-256 header in webhook request")
        return False

    if not signature_header.startswith("sha256="):
        logger.warning("Malformed signature header prefix", header=signature_header)
        return False

    expected_sig = signature_header.split("sha256=", 1)[1]
    calculated_sig = hmac.HMAC(
        key=app_secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    is_valid = hmac.compare_digest(calculated_sig, expected_sig)
    if not is_valid:
        logger.warning("WhatsApp webhook signature verification failed")

    return is_valid
