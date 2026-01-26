from bria_client.clients.settings import BriaSettings
from bria_client.engines.api_engine import AdditionalHeaders, ApiEngine
from bria_client.toolkit.models import BriaResponse


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

    def post(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs) -> BriaResponse:
        api_token = kwargs.pop("api_token", self._api_token)
        old_token = self._api_token
        try:
            self._api_token = api_token
            return super().post(endpoint=endpoint, payload=payload, headers=headers, **kwargs)
        finally:
            self._api_token = old_token

    def get(self, endpoint: str, headers: dict | None = None, **kwargs) -> BriaResponse:
        api_token = kwargs.pop("api_token", self._api_token)
        old_token = self._api_token
        try:
            self._api_token = api_token
            return super().get(endpoint=endpoint, headers=headers, **kwargs)
        finally:
            self._api_token = old_token

    async def post_async(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs) -> BriaResponse:
        api_token = kwargs.pop("api_token", self._api_token)
        old_token = self._api_token
        try:
            self._api_token = api_token
            return await super().post_async(endpoint=endpoint, payload=payload, headers=headers, **kwargs)
        finally:
            self._api_token = old_token

    async def get_async(self, endpoint: str, headers: dict | None = None, **kwargs) -> BriaResponse:
        api_token = kwargs.pop("api_token", self._api_token)
        old_token = self._api_token
        try:
            self._api_token = api_token
            return await super().get_async(endpoint=endpoint, headers=headers, **kwargs)
        finally:
            self._api_token = old_token
