from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Literal

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
    def default_headers(self) -> dict[str, str]:
        return {name: get_header() if callable(get_header) else get_header for name, get_header in self._default_headers.items()}

    @property
    @abstractmethod
    def auth_headers(self) -> dict[str, str]:
        pass

    def set_http_client(self, http_client: BaseHTTPRequest):
        self.client = http_client

    def sync_request(self, endpoint: str, method: Literal["POST", "GET"], payload: dict | None = None, headers: dict | None = None, **kwargs) -> BriaResponse:
        assert isinstance(self.client, SyncHTTPRequest), "with async client please use .async_request() method"
        url = self._prepare_endpoint(endpoint)
        headers = self._prepare_headers(headers=headers)
        return self.client.request(url=url, method=method, payload=payload, headers=headers, **kwargs)

    async def async_request(
        self, endpoint: str, method: Literal["POST", "GET"], payload: dict | None = None, headers: dict | None = None, **kwargs
    ) -> BriaResponse:
        assert isinstance(self.client, AsyncHTTPRequest), "with sync client please use .sync_request() method"
        url = self._prepare_endpoint(endpoint)
        headers = self._prepare_headers(headers=headers)
        return await self.client.request(url=url, method=method, payload=payload, headers=headers, **kwargs)

    def _prepare_headers(self, headers: dict | None = None) -> dict:
        additional_headers = headers or {}
        return {**self.default_headers, **additional_headers, **self.auth_headers}

    def _prepare_endpoint(self, endpoint: str) -> str:
        return f"{self.base_url}/v2/{endpoint.lstrip('/')}"
