# Testing Rules

Run tests: `uv run pytest` (testpaths configured to `tests/`).

## Structure

- Three categories: `tests/unit/`, `tests/integration/`, `tests/component/`.
- Mirror source directory structure within each category (e.g., `tests/unit/clients/`, `tests/unit/toolkit/`).
- One test class per file. Classes prefixed with `Test`.
- Mark every test class: `@pytest.mark.unit`, `@pytest.mark.integration`, or `@pytest.mark.component`.
- Async tests also need `@pytest.mark.asyncio`.

## Naming

`test_<what>_on_<condition>_should_<expected>`. Drop `_on_<condition>` when trivial.

## Style

- Use `pytest`, `pytest-mock`, `pytest-asyncio` only. No `unittest`.
- Follow Arrange-Act-Assert with section comments:
  ```python
  def test_something(self):
      # Arrange
      ...
      # Act
      ...
      # Assert
      ...
  ```
- Plain `assert` statements. `pytest.raises()` for exceptions.
- One logical assertion per test. Multiple asserts fine if verifying the same behavior.
- Avoid redundant tests — don't write a test implied by a stronger existing test.
- Fixtures go in `conftest.py` at the appropriate level.

## After making changes

1. Run unit + integration tests: `uv run pytest tests/unit/ tests/integration/ -v`
2. Fix failures before considering work complete.
3. Run `uv run pre-commit run --all-files`.
4. Only at the very end, run component tests: `uv run pytest tests/component/ -m component -v`

Skip tests only if: docs-only change, test-file-only change, or user says to.