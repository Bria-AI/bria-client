# TypeScript Style (packages/typescript)

Applies to the `@bria-ai/client` package.

## Tooling

- **ESLint** (flat config, `@typescript-eslint`) + **Prettier** (printWidth 100, double quotes,
  trailing commas). Do not hand-format — run `npm run format`.
- **tsc** strict for type checking (`npm run typecheck`). Build with **tsup** (dual ESM/CJS + d.ts).
- **vitest** for tests (`npm run test`). Node 18+ runtime (global `fetch`/`FormData`/`Blob`).

## Conventions

- ESM source. Use explicit `.js` extensions on relative imports (bundler/NodeNext resolution).
- `type`-only imports use `import type`. Public API signatures fully typed; avoid `any` in the
  public surface (internal `any` is allowed where the API is intentionally open, e.g. `BriaResult`).
- Mirror the Python SDK's module boundaries (`client`, `engine`, `settings`, `toolkit/*`) and
  method names (`run`/`submit`/`get`/`upload`/`status`/`poll`) so the two stay recognizable.
  When you change shared behavior here, make the matching change in the Python SDK.

## Testing

- Mock network with `vi.stubGlobal("fetch", …)`. No live API calls in unit tests.
