import pytest

from bria_client.engines.api_engine import ApiEngine


class _ConcreteApiEngine(ApiEngine):
    @property
    def auth_headers(self) -> dict[str, str]:
        return {}

    def _check_auth_override(self, kwargs: dict) -> dict[str, str] | None:
        return None


@pytest.fixture
def api_engine() -> ApiEngine:
    return _ConcreteApiEngine(base_url="")
