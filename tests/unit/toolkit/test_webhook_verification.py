import base64
import hashlib
import hmac

import pytest

from bria_client.toolkit.webhook_verification import verify_webhook_signature

API_TOKEN = "test-api-token"
WEBHOOK_ID = "req_abc123"
TIMESTAMP = "1700000000"
PAYLOAD = b'{"status":"COMPLETED","request_id":"req_abc123"}'


def _make_signature(api_token: str, webhook_id: str, timestamp: str, payload: bytes) -> str:
    signing_key = hmac.new(api_token.encode(), b"bria-webhook-signing-v1", hashlib.sha256).digest()
    message = f"{webhook_id}.{timestamp}.{payload.decode()}".encode()
    sig = base64.b64encode(hmac.new(signing_key, message, hashlib.sha256).digest()).decode()
    return f"v1={sig}"


@pytest.mark.unit
class TestVerifyWebhookSignature:
    def test_valid_signature_returns_true(self):
        header = _make_signature(API_TOKEN, WEBHOOK_ID, TIMESTAMP, PAYLOAD)
        assert verify_webhook_signature(PAYLOAD, WEBHOOK_ID, TIMESTAMP, header, API_TOKEN) is True

    def test_tampered_payload_returns_false(self):
        header = _make_signature(API_TOKEN, WEBHOOK_ID, TIMESTAMP, PAYLOAD)
        tampered = b'{"status":"FAILED","request_id":"req_abc123"}'
        assert verify_webhook_signature(tampered, WEBHOOK_ID, TIMESTAMP, header, API_TOKEN) is False

    def test_wrong_api_token_returns_false(self):
        header = _make_signature(API_TOKEN, WEBHOOK_ID, TIMESTAMP, PAYLOAD)
        assert verify_webhook_signature(PAYLOAD, WEBHOOK_ID, TIMESTAMP, header, "wrong-token") is False

    def test_tampered_webhook_id_returns_false(self):
        header = _make_signature(API_TOKEN, WEBHOOK_ID, TIMESTAMP, PAYLOAD)
        assert verify_webhook_signature(PAYLOAD, "req_other", TIMESTAMP, header, API_TOKEN) is False

    def test_tampered_timestamp_returns_false(self):
        header = _make_signature(API_TOKEN, WEBHOOK_ID, TIMESTAMP, PAYLOAD)
        assert verify_webhook_signature(PAYLOAD, WEBHOOK_ID, "9999999999", header, API_TOKEN) is False

    def test_multiple_tokens_one_valid_returns_true(self):
        valid = _make_signature(API_TOKEN, WEBHOOK_ID, TIMESTAMP, PAYLOAD)
        header = f"v1=invalidsig,{valid}"
        assert verify_webhook_signature(PAYLOAD, WEBHOOK_ID, TIMESTAMP, header, API_TOKEN) is True

    def test_multiple_tokens_all_invalid_returns_false(self):
        header = "v1=invalidsig1, v1=invalidsig2"
        assert verify_webhook_signature(PAYLOAD, WEBHOOK_ID, TIMESTAMP, header, API_TOKEN) is False

    def test_token_with_whitespace_is_handled(self):
        valid = _make_signature(API_TOKEN, WEBHOOK_ID, TIMESTAMP, PAYLOAD)
        header = f"  {valid}  "
        assert verify_webhook_signature(PAYLOAD, WEBHOOK_ID, TIMESTAMP, header, API_TOKEN) is True

    def test_empty_signature_header_returns_false(self):
        assert verify_webhook_signature(PAYLOAD, WEBHOOK_ID, TIMESTAMP, "", API_TOKEN) is False
