import json
from pathlib import Path

import pytest


def _find_contract_dir() -> Path:
    """Walk up from this file until we find the repo-root `contract/` directory."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "contract"
        if (candidate / "constants.json").is_file():
            return candidate
    raise FileNotFoundError("Could not locate the repo-root contract/ directory")


CONTRACT_DIR = _find_contract_dir()


def load_contract(relative_path: str) -> dict:
    return json.loads((CONTRACT_DIR / relative_path).read_text())


@pytest.fixture(scope="session")
def load_contract_fixture():
    return load_contract


@pytest.fixture(scope="session")
def contract_constants() -> dict:
    return load_contract("constants.json")
