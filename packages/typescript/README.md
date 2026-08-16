# @bria-ai/client

TypeScript/JavaScript SDK for the [Bria](https://bria.ai) Engine API — image & video editing.

Requires **Node.js 18+** (uses the built-in `fetch`, `FormData`, and `Blob`).

## Install

```bash
npm install @bria-ai/client
```

## Usage

```ts
import { BriaClient } from "@bria-ai/client";

const client = new BriaClient({ apiToken: process.env.BRIA_API_TOKEN });

// Synchronous job — resolves when it's done:
const res = await client.run(
  "remove_background",
  { image_url: "https://example.com/cat.png" },
  { raiseForStatus: true },
);
console.log(res.result);

// Asynchronous job — submit then poll:
const submitted = await client.submit("increase_resolution", { image_url: "https://…" });
const done = await client.poll(submitted, { interval: 2, timeout: 120 });
```

`apiToken` and `baseUrl` also fall back to the `BRIA_API_TOKEN` / `BRIA_BASE_URL` environment
variables.

## API surface

| Method                             | Purpose                                                     |
| ---------------------------------- | ----------------------------------------------------------- |
| `run(endpoint, payload, opts?)`    | Run a synchronous job (`sync: true`).                       |
| `submit(endpoint, payload, opts?)` | Submit an async job (`sync: false`); optional `webhookUrl`. |
| `get(endpoint, opts?)`             | Raw GET with optional `params`.                             |
| `upload(source, opts?)`            | Upload a local file/bytes, returns a `file_url`.            |
| `status(requestId, opts?)`         | Current `Status` of a job.                                  |
| `poll(target, opts?)`              | Poll until terminal (`interval`/`timeout` in seconds).      |

Toolkit exports: `BriaResponse`, `Status`, `BriaException`, `Image`, `verifyWebhookSignature`.

## Differences from the Python SDK

- **Async only.** JavaScript has no synchronous HTTP, so there is a single `BriaClient` (no
  sync/async client split). `run` vs `submit` still map to the API's `sync` flag.
- **`Image`** accepts a URL, data URI, base64 string, local path, or `Buffer`/`Uint8Array`
  (and `Image.fromBlob` for a `Blob`). It does not accept PIL images or numpy arrays.

Shared behavior (auth, retries, endpoint normalization, webhook signing, status parsing) is
pinned by the repo-root [`contract/`](../../contract) and verified in both SDKs' test suites.

## Webhook verification

```ts
import { verifyWebhookSignature } from "@bria-ai/client";

const ok = verifyWebhookSignature({
  payload: rawBodyString,
  webhookId: req.headers["bria-webhook-id"],
  timestamp: req.headers["bria-webhook-timestamp"],
  signatureHeader: req.headers["bria-webhook-signature"],
  apiToken: process.env.BRIA_API_TOKEN,
});
```

## License

MIT
