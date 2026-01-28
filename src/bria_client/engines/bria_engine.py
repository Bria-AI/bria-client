from bria_client.clients.settings import BriaSettings
from bria_client.engines.api_engine import AdditionalHeaders, ApiEngine


class BriaEngine(ApiEngine):
    def __init__(
        self,
        base_url: str | None,
        api_token: str | None = None,
        default_headers: AdditionalHeaders | None = None,
    ):
        self.settings = BriaSettings()
        self._api_token = api_token or self.settings.api_token
        base_url = base_url or self.settings.base_url
        super().__init__(base_url=base_url, default_headers=default_headers)

    @property
    def auth_headers(self) -> dict[str, str]:
        if self._api_token is None:
            raise ValueError("api_token is required, please set BRIA_API_TOKEN or pass it explicitly to method")
        return {"api_token": self._api_token}

    def _check_auth_override(self, kwargs: dict) -> dict[str, str] | None:
        api_token = kwargs.pop("api_token", self._api_token)
        auth_override = {"api_token": api_token} if api_token else None
        return auth_override
