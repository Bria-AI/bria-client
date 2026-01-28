from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Literal

from bria_client.engines.base.async_http_request import AsyncHTTPRequest
from bria_client.engines.base.base_http_request import BaseHTTPRequest
from bria_client.engines.base.sync_http_request import SyncHTTPRequest
from bria_client.toolkit import BriaResponse

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

    @abstractmethod
    def _check_auth_override(self, kwargs: dict) -> dict[str, str] | None:
        """method to check auth override to be passed to the engine.
        It enables the ability to override the default auth headers for each method call (through the kwargs)
        """
        pass

    def set_http_client(self, http_client: BaseHTTPRequest):
        self.client = http_client

    # region SyncClient related methods
    def post(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs) -> BriaResponse:
        auth_override = self._check_auth_override(kwargs=kwargs)
        return self.sync_request(endpoint=endpoint, method="POST", payload=payload, headers=headers, auth_override=auth_override, **kwargs)

    def get(self, endpoint: str, headers: dict | None = None, **kwargs) -> BriaResponse:
        auth_override = self._check_auth_override(kwargs=kwargs)
        return self.sync_request(endpoint=endpoint, method="GET", headers=headers, auth_override=auth_override, **kwargs)

    def sync_request(
        self,
        endpoint: str,
        method: Literal["POST", "GET"],
        payload: dict | None = None,
        headers: dict | None = None,
        auth_override: dict[str, str] | None = None,
        **kwargs,
    ) -> BriaResponse:
        assert isinstance(self.client, SyncHTTPRequest), "with async client please use .async_request() method"
        url = self._prepare_endpoint(endpoint)
        headers = self._prepare_headers(headers=headers, auth_override=auth_override)
        return self.client.request(url=url, method=method, payload=payload, headers=headers, **kwargs)

    # endregion

    # region AsyncClient related methods
    async def post_async(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs) -> BriaResponse:
        auth_override = self._check_auth_override(kwargs=kwargs)
        return await self.async_request(endpoint=endpoint, method="POST", payload=payload, headers=headers, auth_override=auth_override, **kwargs)

    async def get_async(self, endpoint: str, headers: dict | None = None, **kwargs) -> BriaResponse:
        auth_override = self._check_auth_override(kwargs=kwargs)
        return await self.async_request(endpoint=endpoint, method="GET", headers=headers, auth_override=auth_override, **kwargs)

    async def async_request(
        self,
        endpoint: str,
        method: Literal["POST", "GET"],
        payload: dict | None = None,
        headers: dict | None = None,
        auth_override: dict[str, str] | None = None,
        **kwargs,
    ) -> BriaResponse:
        assert isinstance(self.client, AsyncHTTPRequest), "with sync client please use .sync_request() method"
        url = self._prepare_endpoint(endpoint)
        headers = self._prepare_headers(headers=headers, auth_override=auth_override)
        return await self.client.request(url=url, method=method, payload=payload, headers=headers, **kwargs)

    # endregion

    def _prepare_headers(self, headers: dict | None = None, auth_override: dict[str, str] | None = None) -> dict:
        additional_headers = headers or {}
        auth = auth_override if auth_override is not None else self.auth_headers
        return {**self.default_headers, **additional_headers, **auth}

    def _prepare_endpoint(self, endpoint: str) -> str:
        return f"{self.base_url}/v2/{endpoint.lstrip('/')}"
