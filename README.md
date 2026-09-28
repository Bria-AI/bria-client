# Bria SDKs

Official SDKs for the [Bria](https://bria.ai) Engine API — image & video editing. This is a
monorepo containing one SDK per language.

## Packages

| Package | Language | Install |
| --- | --- | --- |
| [`packages/python`](packages/python) | Python 3.10+ | `pip install bria-client` |
| [`packages/typescript`](packages/typescript) | TypeScript / Node 18+ | `npm install @bria-ai/client` |

The SDKs are hand-written (not generated from a spec) and deliberately mirror each other —
same method names (`run`/`submit`/`get`/`upload`/`status`/`poll`), same toolkit, same behavior
(auth, retry/poll defaults, response/status parsing, webhook verification). When you change
shared behavior in one SDK, make the matching change in the other.

## Layout

```
packages/
  python/            # Python SDK (uv + hatchling)
  typescript/        # TypeScript SDK (npm + tsup)
```

## Development

Each package is self-contained — see its README for setup.

```bash
# Python
cd packages/python && uv sync && uv run pytest tests/unit tests/integration -v

# TypeScript
cd packages/typescript && npm ci && npm run build && npm test
```

Whole-repo checks (from the repo root):

```bash
uv run --project packages/python pre-commit run --all-files
```

## Releases

Releases are automated with release-please (see `release-please-config.json`). The Python
package tags as `vX.Y.Z`; the TypeScript package tags as `@bria-ai/client-vX.Y.Z`. Merging a
release PR publishes that package (PyPI / npm) via `.github/workflows/publish.yml`.

## License

MIT — see [LICENSE](LICENSE).
