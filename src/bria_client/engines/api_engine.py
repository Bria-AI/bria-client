from abc import ABC, abstractmethod
from collections.abc import Callable

from bria_client.engines.base.async_http_request import AsyncHTTPRequest
from bria_client.engines.base.base_http_request import BaseHTTPRequest
from bria_client.engines.base.sync_http_request import SyncHTTPRequest
from bria_client.toolkit.models import BriaResponse

AdditionalHeaders = dict[str, str | Callable[[], str]]


class ApiEngine(ABC):
    def __init__(self, base_url: str | None, default_headers: AdditionalHeaders | None = None):
        self.base_url = base_url
        self._default_headers = default_headers or {}
        self.client: BaseHTTPRequest | None = None

    @property
    @abstractmethod
    def auth_headers(self) -> dict[str, str]:
        pass

    def set_http_client(self, http_client: BaseHTTPRequest):
        self.client = http_client

    # region SYNC HTTP METHODS
    def post(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs) -> BriaResponse:
        assert isinstance(self.client, SyncHTTPRequest), "with async client please use .post_async() method"
        url = self.prepare_endpoint(endpoint)
        headers = self.prepare_headers(headers=headers)
        return self.client.post(url=url, payload=payload, headers=headers)

    def get(self, endpoint: str, headers: dict | None = None, **kwargs) -> BriaResponse:
        assert isinstance(self.client, SyncHTTPRequest), "with async client please use .post_async() method"
        url = self.prepare_endpoint(endpoint)
        headers = self.prepare_headers(headers=headers)
        return self.client.get(url=url, headers=headers)

    # endregion
    # region ASYNC HTTP METHODS
    async def post_async(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs) -> BriaResponse:
        assert isinstance(self.client, AsyncHTTPRequest), "with sync client please use .post() method"
        url = self.prepare_endpoint(endpoint)
        headers = self.prepare_headers(headers=headers)
        return await self.client.post(url=url, payload=payload, headers=headers)

    async def get_async(self, endpoint: str, headers: dict | None = None, **kwargs) -> BriaResponse:
        assert isinstance(self.client, AsyncHTTPRequest), "with sync client please use .get() method"
        url = self.prepare_endpoint(endpoint)
        headers = self.prepare_headers(headers=headers)
        return await self.client.get(url=url, headers=headers)

    # endregion

    @property
    def default_headers(self) -> dict[str, str]:
        return {name: get_header() if callable(get_header) else get_header for name, get_header in self._default_headers.items()}

    def prepare_headers(self, headers: dict | None = None) -> dict:
        additional_headers = headers or {}
        return {**self.default_headers, **additional_headers, **self.auth_headers}

    def prepare_endpoint(self, endpoint: str) -> str:
        return f"{self.base_url}/v2/{endpoint.lstrip('/')}"
