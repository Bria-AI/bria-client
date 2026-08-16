# Bria SDK contract

This directory is the **single source of truth** for behavior that every Bria SDK
(`packages/python`, `packages/typescript`, and any future language) must share. Its purpose
is to stop the SDKs from drifting apart.

## Files

- **`constants.json`** — shared constants: API version prefix, default base URL, auth header
  name, User-Agent template, retry/poll defaults, the `sync` flag semantics, well-known
  endpoints, the `Status` enum values, and the webhook signing scheme.
- **`fixtures/`** — golden cases each SDK replays in its own test suite:
  - `response-parsing.json` — status derivation from a raw response body.
  - `http-error.json` — synthesizing a `BriaError` from a failing HTTP response.
  - `upload-response.json` — shape of the `video/upload` presigned response.
  - `endpoint-normalization.json` — how an endpoint string becomes a full URL.
  - `payload-null-stripping.json` — which payload keys are dropped before sending.
  - `user-agent.json` — the rendered User-Agent string per language.
  - `webhook.json` — deterministic HMAC-SHA256 verification vectors.

## Rules

1. **Edit here first.** A behavior change (new default, renamed header, new status value)
   starts as an edit to `constants.json` / `fixtures/`.
2. **Every SDK must stay green** against these files. Each package has contract tests that
   load this directory and assert their implementation matches. A change here that an SDK
   hasn't adopted yet fails that SDK's CI — which is exactly the drift alarm we want.
3. **Keep fixtures language-agnostic.** Plain JSON, no per-language encoding. `null` means
   Python `None` / JS `null`.
4. The webhook vectors in `webhook.json` are real signatures. If you change the signing
   scheme, regenerate them (see `constants.json#webhook`).
