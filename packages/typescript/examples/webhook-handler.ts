/**
 * Bria webhook handler (dependency-free, uses node:http).
 *
 * Demonstrates:
 *   1. Starting an HTTP endpoint that receives and *verifies* a signed Bria webhook.
 *   2. Submitting an async job with a `webhookUrl` so Bria POSTs the result on completion.
 *
 * Run:  BRIA_API_TOKEN=... WEBHOOK_URL=https://your-public-host/webhook npx tsx examples/webhook-handler.ts
 *
 * For local development, expose localhost with a tunnel (e.g. `ngrok http 8000`) and pass the
 * public URL as WEBHOOK_URL.
 */
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

import { BriaClient, verifyWebhookSignature } from "@bria-ai/client";

const PORT = Number(process.env.PORT ?? 8000);
const API_TOKEN = process.env.BRIA_API_TOKEN ?? "";

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (c: Buffer) => chunks.push(c));
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf-8")));
    req.on("error", reject);
  });
}

async function handleWebhook(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const body = await readBody(req);
  const header = (name: string): string => {
    const v = req.headers[name.toLowerCase()];
    return Array.isArray(v) ? (v[0] ?? "") : (v ?? "");
  };

  const valid = verifyWebhookSignature({
    payload: body,
    webhookId: header("Bria-Webhook-Id"),
    timestamp: header("Bria-Webhook-Timestamp"),
    signatureHeader: header("Bria-Webhook-Signature"),
    apiToken: API_TOKEN,
  });

  if (!valid) {
    res.writeHead(401).end("invalid signature");
    console.warn("Rejected a webhook with an invalid signature");
    return;
  }

  console.log("Verified webhook:", body);
  res.writeHead(200).end("ok");
}

const server = createServer((req, res) => {
  if (req.method === "POST" && req.url === "/webhook") {
    handleWebhook(req, res).catch((err) => {
      console.error(err);
      res.writeHead(500).end("error");
    });
  } else {
    res.writeHead(404).end();
  }
});

server.listen(PORT, () => {
  console.log(`Listening for webhooks on http://localhost:${PORT}/webhook`);

  const webhookUrl = process.env.WEBHOOK_URL;
  if (webhookUrl) {
    const client = new BriaClient({ apiToken: API_TOKEN });
    client
      .submit(
        "image/edit/remove_background",
        { image: "https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png" },
        { webhookUrl },
      )
      .then((r) => console.log("Submitted job:", r.requestId))
      .catch((err) => console.error("Submit failed:", err));
  } else {
    console.log("Set WEBHOOK_URL to also submit a job that calls back to this server.");
  }
});
