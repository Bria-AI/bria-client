# CLAUDE.md

## Package

`bria-client` — Python SDK for the Bria Engine API. Sync + async clients for image/video editing.

- Import: `from bria_client import BriaSyncClient, BriaAsyncClient`
- Build: hatchling + uv-dynamic-versioning
- Deps: httpx, pydantic, pydantic-settings, pillow, numpy, werkzeug

## Source layout

```
src/bria_client/
  clients/       → BriaSyncClient, BriaAsyncClient, BaseBriaClient, BriaSettings
  engines/       → ApiEngine (abstract), BriaEngine, base/ (HTTP layer)
  toolkit/       → Image, BriaResponse, BriaResult, BriaError, Status, BriaException
tests/           → unit/, integration/, component/
examples/
```

## Environment

- Python 3.10+, package manager: uv, run via `uv run`
- Setup: `uv sync`
- `BRIA_API_TOKEN` — required for e2e tests
- `BRIA_BASE_URL` — defaults to `https://engine.prod.bria-api.com`

## Code quality

All changes must pass `pre-commit run --all-files` before committing.