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
