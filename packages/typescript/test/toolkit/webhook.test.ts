import { createHmac } from "node:crypto";
import { describe, expect, it } from "vitest";

import { verifyWebhookSignature } from "../../src/toolkit/webhook.js";

const API_TOKEN = "test-token-abc123";
const WEBHOOK_ID = "req-9f8e7d6c";
const TIMESTAMP = "1723800000";
const PAYLOAD = '{"request_id":"req-9f8e7d6c","status":"COMPLETED"}';

/** Independently sign a payload the same way the Bria backend does. */
function sign(payload: string, webhookId: string, timestamp: string, apiToken: string): string {
  const key = createHmac("sha256", apiToken).update("bria-webhook-signing-v1").digest();
  return createHmac("sha256", key).update(`${webhookId}.${timestamp}.${payload}`).digest("base64");
}

// Shared cross-repo contract vector (see packages/python/tests/unit/toolkit/test_webhook_verification.py).
// Both SDKs and the backend must agree on this exact signature.
const CONTRACT = {
  apiToken: "contract-test-shared-token",
  webhookId: "req_contract_test_001",
  timestamp: "1700000000",
  payload:
    '{"status":"COMPLETED","result":{"url":"https://cdn.bria.ai/final.png"},"request_id":"req_contract_test_001"}',
  signatureHeader: "v1=muClfnkuIXEqW69htILKVEwJdzC0LWB1tP53ptLm7SM=",
};

describe("verifyWebhookSignature shared contract vector", () => {
  it("verifies the vector shared with the Python SDK and the backend", () => {
    expect(verifyWebhookSignature(CONTRACT)).toBe(true);
  });
});

describe("verifyWebhookSignature", () => {
  const validSig = sign(PAYLOAD, WEBHOOK_ID, TIMESTAMP, API_TOKEN);

  it("accepts a valid signature", () => {
    expect(
      verifyWebhookSignature({
        payload: PAYLOAD,
        webhookId: WEBHOOK_ID,
        timestamp: TIMESTAMP,
        signatureHeader: `v1=${validSig}`,
        apiToken: API_TOKEN,
      }),
    ).toBe(true);
  });

  it("accepts when one of several tokens is valid", () => {
    expect(
      verifyWebhookSignature({
        payload: PAYLOAD,
        webhookId: WEBHOOK_ID,
        timestamp: TIMESTAMP,
        signatureHeader: `v1=deadbeef, v1=${validSig}`,
        apiToken: API_TOKEN,
      }),
    ).toBe(true);
  });

  it("rejects a tampered payload", () => {
    expect(
      verifyWebhookSignature({
        payload: PAYLOAD.replace("COMPLETED", "FAILED"),
        webhookId: WEBHOOK_ID,
        timestamp: TIMESTAMP,
        signatureHeader: `v1=${validSig}`,
        apiToken: API_TOKEN,
      }),
    ).toBe(false);
  });

  it("rejects an empty signature header", () => {
    expect(
      verifyWebhookSignature({
        payload: PAYLOAD,
        webhookId: WEBHOOK_ID,
        timestamp: TIMESTAMP,
        signatureHeader: "",
        apiToken: API_TOKEN,
      }),
    ).toBe(false);
  });

  it("accepts a Uint8Array payload identically", () => {
    expect(
      verifyWebhookSignature({
        payload: new TextEncoder().encode(PAYLOAD),
        webhookId: WEBHOOK_ID,
        timestamp: TIMESTAMP,
        signatureHeader: `v1=${validSig}`,
        apiToken: API_TOKEN,
      }),
    ).toBe(true);
  });
});
