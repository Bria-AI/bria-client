# CLAUDE.md

## Monorepo

SDKs for the Bria Engine API, one package per language, plus a shared behavioral contract.

```
contract/            → shared constants.json + fixtures/ (single source of truth; the drift guard)
packages/
  python/            → bria-client (Python SDK)
  typescript/        → @bria-ai/client (TypeScript SDK)
```

**Keeping SDKs in sync:** the SDKs are hand-written. `contract/` pins behavior every SDK must
implement identically (auth, endpoint normalization, retry/poll defaults, response/status
parsing, webhook verification). Each SDK has contract tests that load `contract/` and fail on
drift. Change a shared behavior in `contract/` first, then make every SDK green.

## Python package (`packages/python`)

`bria-client` — sync + async clients for image/video editing.

- Import: `from bria_client import BriaSyncClient, BriaAsyncClient`
- Build: hatchling + uv-dynamic-versioning. Deps: httpx, pydantic, pydantic-settings, pillow, numpy, werkzeug
- Layout: `src/bria_client/{clients,engines,toolkit}/`, `tests/{unit,integration,component}/`, `examples/`
- Env: Python 3.10+, uv (`cd packages/python && uv sync`); run via `uv run`

## TypeScript package (`packages/typescript`)

`@bria-ai/client` — a single async `BriaClient` (no sync/async split; JS HTTP is always async).

- Build: npm + tsup (dual ESM/CJS). Test: vitest. Node 18+ (uses global `fetch`).
- Layout: `src/{client,engine,settings}.ts`, `src/toolkit/`, `test/`
- Setup: `cd packages/typescript && npm ci`; then `npm run build|typecheck|lint|test`

## Environment

- `BRIA_API_TOKEN` — required for e2e tests
- `BRIA_BASE_URL` — defaults to `https://engine.prod.bria-api.com`

## Code quality

All changes must pass pre-commit before committing. From the repo root:
`uv run --project packages/python pre-commit run --all-files` (TS hooks require `npm ci` in `packages/typescript`).