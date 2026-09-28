/**
 * Customizing the client: a non-default base URL, default headers sent on every request, a
 * custom retry policy, and a per-call API token override.
 */
import { BriaClient } from "@bria-ai/client";

async function main(): Promise<void> {
  const client = new BriaClient({
    baseUrl: "https://engine.prod.bria-api.com",
    apiToken: process.env.BRIA_API_TOKEN ?? null,
    defaultHeaders: { "x-my-app": "example-app" },
    retry: { total: 5, backoffFactor: 1 },
  });

  // Override the token for a single call (e.g. multi-tenant usage):
  const response = await client.run(
    "image/edit/remove_background",
    { image: "https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png" },
    { apiToken: process.env.OTHER_TENANT_TOKEN ?? undefined },
  );
  console.log(response.status);

  // A raw GET with query params also works:
  const status = await client.status(response.requestId);
  console.log("status:", status);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
