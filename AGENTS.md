Project rules live in `.agents/rules/`. Read and apply each:

- `.agents/rules/**`

## Agent Configuration

All agent rules are canonical in `.agents/rules/`. Each tool's files are thin stubs that point
back to them, so every agent shares one source of truth:

```
.agents/
└── rules/    Always-on rules — loaded by all agents on startup
```

| Tool        | Rules                                                              |
| ----------- | ----------------------------------------------------------------- |
| Claude Code | `CLAUDE.md` → `@AGENTS.md`; `.claude/rules/` stubs → `.agents/rules/` |
| Cursor      | `.cursor/rules/*.mdc` (alwaysApply: true) → `.agents/rules/`       |

To add a rule: create it in `.agents/rules/`, then add the matching stubs under `.claude/rules/`
and `.cursor/rules/`.

## Overview

SDKs for the Bria Engine API — a monorepo, one package per language.

```
python/            → bria-client (Python SDK)
typescript/        → @bria-ai/client (TypeScript SDK)
```

**Keeping SDKs in sync:** the SDKs are hand-written and deliberately mirror each other (same
method names, toolkit, and behavior — auth, retry/poll defaults, response/status parsing,
webhook verification). When changing shared behavior in one SDK, make the matching change in
the other.

### Python package (`python`)

`bria-client` — sync + async clients for image/video editing.

- Import: `from bria_client import BriaSyncClient, BriaAsyncClient`
- Build: hatchling + uv-dynamic-versioning. Deps: httpx, pydantic, pydantic-settings, pillow, numpy, werkzeug
- Layout: `src/bria_client/{clients,engines,toolkit}/`, `tests/{unit,integration,component}/`, `examples/`
- Env: Python 3.10+, uv (`cd python && uv sync`); run via `uv run`

### TypeScript package (`typescript`)

`@bria-ai/client` — a single async `BriaClient` (no sync/async split; JS HTTP is always async).

- Build: npm + tsup (dual ESM/CJS). Test: vitest. Node 20+ (uses global `fetch`).
- Layout: `src/{client,engine,settings}.ts`, `src/toolkit/`, `test/`
- Setup: `cd typescript && npm ci`; then `npm run build|typecheck|lint|test`

## Environment

- `BRIA_API_TOKEN` — required for e2e tests
- `BRIA_BASE_URL` — defaults to `https://engine.prod.bria-api.com`

## Code quality

All changes must pass pre-commit before committing. From the repo root:
`uv run --project python pre-commit run --all-files` (TS hooks require `npm ci` in `typescript`).
