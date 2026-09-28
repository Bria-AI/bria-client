import { createHmac, timingSafeEqual } from "node:crypto";

const WEBHOOK_SIGNING_SALT = "bria-webhook-signing-v1";

/**
 * Verify an inbound Bria webhook using HMAC-SHA256.
 *
 * The signing key is derived from your API token; the signed message is
 * `${webhookId}.${timestamp}.${payload}`. The signature header is a comma-separated list of
 * `v1=<base64>` tokens — verification passes if any one of them matches. Byte-for-byte
 * compatible with the Python SDK's `verify_webhook_signature`.
 *
 * @param payload           Raw request body (string or bytes).
 * @param webhookId         Value of the `Bria-Webhook-Id` header.
 * @param timestamp         Value of the `Bria-Webhook-Timestamp` header.
 * @param signatureHeader   Value of the `Bria-Webhook-Signature` header.
 * @param apiToken          Your Bria API token — used to derive the signing key.
 */
export function verifyWebhookSignature(args: {
  payload: string | Uint8Array;
  webhookId: string;
  timestamp: string;
  signatureHeader: string;
  apiToken: string;
}): boolean {
  const signingKey = createHmac("sha256", args.apiToken).update(WEBHOOK_SIGNING_SALT).digest();
  const payloadStr =
    typeof args.payload === "string" ? args.payload : Buffer.from(args.payload).toString();
  const message = `${args.webhookId}.${args.timestamp}.${payloadStr}`;
  const expected = createHmac("sha256", signingKey).update(message).digest("base64");
  const expectedBuf = Buffer.from(expected);

  for (const rawToken of args.signatureHeader.split(",")) {
    const token = rawToken.trim();
    if (token.startsWith("v1=")) {
      const candidate = Buffer.from(token.slice(3));
      if (candidate.length === expectedBuf.length && timingSafeEqual(candidate, expectedBuf)) {
        return true;
      }
    }
  }
  return false;
}
