import base64
import hashlib
import hmac

import pytest

from bria_client.toolkit.webhook_verification import verify_webhook_signature, WEBHOOK_SIGNING_SALT

API_TOKEN = "test-api-token"
WEBHOOK_ID = "req_abc123"
TIMESTAMP = "1700000000"
PAYLOAD = b'{"status":"COMPLETED","request_id":"req_abc123"}'


def _make_signature(api_token: str, webhook_id: str, timestamp: str, payload: bytes) -> str:
    signing_key = hmac.new(api_token.encode(), WEBHOOK_SIGNING_SALT, hashlib.sha256).digest()
    message = f"{webhook_id}.{timestamp}.{payload.decode()}".encode()
    sig = base64.b64encode(hmac.new(signing_key, message, hashlib.sha256).digest()).decode()
    return f"v1={sig}"


@pytest.mark.unit
class TestVerifyWebhookSignature:
    def test_valid_signature_returns_true(self):
        header = _make_signature(API_TOKEN, WEBHOOK_ID, TIMESTAMP, PAYLOAD)
        assert verify_webhook_signature(PAYLOAD, WEBHOOK_ID, TIMESTAMP, header, API_TOKEN) is True

    @pytest.mark.parametrize(
        "payload,webhook_id,timestamp,api_token",
        [
            (b'{"status":"FAILED"}', WEBHOOK_ID, TIMESTAMP, API_TOKEN),
            (PAYLOAD, "req_other", TIMESTAMP, API_TOKEN),
            (PAYLOAD, WEBHOOK_ID, "9999999999", API_TOKEN),
            (PAYLOAD, WEBHOOK_ID, TIMESTAMP, "wrong-token"),
        ],
    )
    def test_invalid_input_returns_false(self, payload, webhook_id, timestamp, api_token):
        header = _make_signature(API_TOKEN, WEBHOOK_ID, TIMESTAMP, PAYLOAD)
        assert verify_webhook_signature(payload, webhook_id, timestamp, header, api_token) is False

    def test_multiple_signatures_one_valid_returns_true(self):
        valid = _make_signature(API_TOKEN, WEBHOOK_ID, TIMESTAMP, PAYLOAD)
        header = f"v1=invalidsig,{valid}"
        assert verify_webhook_signature(PAYLOAD, WEBHOOK_ID, TIMESTAMP, header, API_TOKEN) is True

    def test_empty_signature_header_returns_false(self):
        assert verify_webhook_signature(PAYLOAD, WEBHOOK_ID, TIMESTAMP, "", API_TOKEN) is False
