import base64
import hashlib
import hmac

WEBHOOK_SIGNING_SALT = b"bria-webhook-signing-v1"


def _derive_signing_key(api_token: str) -> bytes:
    return hmac.new(
        api_token.encode(),
        WEBHOOK_SIGNING_SALT,
        hashlib.sha256,
    ).digest()


def verify_webhook_signature(
    payload: bytes,
    webhook_id: str,
    timestamp: str,
    signature_header: str,
    api_token: str,
) -> bool:
    """
    Verify an inbound Bria webhook using HMAC-SHA256.

    Args:
        payload:          Raw request body bytes.
        webhook_id:       Value of the ``Bria-Webhook-Id`` header (the job's request_id).
        timestamp:        Value of the ``Bria-Webhook-Timestamp`` header (Unix epoch string).
        signature_header: Value of the ``Bria-Webhook-Signature`` header
                          (comma-separated ``v1=<base64>`` tokens).
        api_token:        Your Bria API token — used to derive the signing key.

    Returns:
        ``True`` if at least one token in the signature header is valid, ``False`` otherwise.
    """
    signing_key = _derive_signing_key(api_token)
    message = f"{webhook_id}.{timestamp}.{payload.decode()}".encode()
    expected = base64.b64encode(hmac.new(signing_key, message, hashlib.sha256).digest()).decode()

    for token in signature_header.split(","):
        token = token.strip()
        if token.startswith("v1="):
            candidate = token[3:]
            if hmac.compare_digest(candidate, expected):
                return True
    return False
