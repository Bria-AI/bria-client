# Code Style

## Formatting & Linting

- **Ruff** for formatting and linting. Do not use black, isort, or flake8.
- **Pyright** for type checking.
- Line length: 160. Target: Python 3.10+.
- Lint rules: `C4`, `E`, `F`, `I`, `PERF`, `UP`. Ignored: `PERF203`, `E402`, `F821`. `F401` ignored in `__init__.py`.

## Pre-commit hooks (fail_fast: true)

1. Gitleaks — secret scanning
2. Prettier — YAML/JSON
3. Commitizen — conventional commits (commit-msg stage)
4. Ruff Format — Python formatting
5. Ruff Check — `--fix --exit-non-zero-on-fix`
6. Pyright — type checking
7. uv lock --check — lock file sync

## Commit messages

Conventional Commits, sentence-case subject. Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

Examples: `feat: Add presigned URL generation`, `fix: Handle missing content-type in image upload`

## Python conventions

- `logging.getLogger(__name__)` at module level.
- Type hints on all public signatures. Use `X | None` (not `Optional[X]`).
- `ABC` + `@abstractmethod` for abstract classes.
- Google-style docstrings (`Args:`, `Returns:`, `Example:`) on public API only.
- Import order handled by Ruff `I` rule: stdlib → third-party → local (`bria_client.*`).