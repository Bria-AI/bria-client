from abc import ABC, abstractmethod
from collections.abc import Callable

from bria_client.engines.base.base_http_request import BaseHTTPRequest
from bria_client.engines.base.sync_http_request import SyncHTTPRequest

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

    def set_http_client(self, http_client: SyncHTTPRequest):
        self.client = http_client

    # region SYNC HTTP METHODS
    def post(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs):
        assert isinstance(self.client, SyncHTTPRequest), "with async client please use .post_async() method"

        return self.client.post(url=self.prepare_endpoint(endpoint), payload=self.prepare_payload(payload), headers=self.prepare_headers(headers=headers))

    def get(self, endpoint: str, headers: dict | None = None, **kwargs):
        assert isinstance(self.client, SyncHTTPRequest), "with async client please use .post_async() method"

        return self.client.get(url=self.prepare_endpoint(endpoint), headers=self.prepare_headers(headers=headers))

    # endregion
    # region ASYNC HTTP METHODS
    async def post_async(self):
        raise NotImplementedError("idk")
        ...

    async def get_async(self):
        raise NotImplementedError("idk")
        ...

    # endregion

    @property
    def default_headers(self) -> dict[str, str]:
        return {name: get_header() if callable(get_header) else get_header for name, get_header in self._default_headers.items()}

    def prepare_headers(self, headers: dict | None = None) -> dict:
        additional_headers = headers or {}
        return {**self.default_headers, **additional_headers, **self.auth_headers}

    def prepare_endpoint(self, endpoint: str) -> str:
        return f"{self.base_url}/v2/{endpoint.lstrip('/')}"

    def prepare_payload(self, payload: dict) -> dict:
        # TODO: here should convert image to base64 if needed
        return payload
