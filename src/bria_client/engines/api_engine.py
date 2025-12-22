from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx
from httpx_retries import Retry

from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.engines.async_http_request import AsyncHTTPRequest
from bria_client.exceptions import MissingAuthenticationException
from bria_client.payloads.bria_payload import BriaPayload
from bria_client.responses import BriaResponse

T = TypeVar("T", bound=BriaResponse)


class ApiEngine(AsyncHTTPRequest):
    """this should be the abstract base class for all engines"""

    def __init__(self, auth_header: dict | Callable[[], dict], base_url: str = None, retry: Retry | None = Retry(total=3, backoff_factor=2)):
        self.base_url = base_url
        self.retry = retry
        self._auth_header = auth_header
        super().__init__(retry=retry)

    @property
    def auth_header(self) -> dict:
        if isinstance(self._auth_header, Callable):
            return self._auth_header()
        return self._auth_header

    @enable_run_synchronously
    async def post(self, url: str, payload: BriaPayload, response_obj: type[T], headers: dict | None = None, **kwargs) -> Awaitable[T] | T:
        if headers is None:
            headers = {}
        if list(self.auth_header.values())[0] is None:
            raise MissingAuthenticationException

        response = await super().post(url, payload=payload.model_dump(exclude_none=True), headers={**headers, **self.auth_header}, **kwargs)
        return response_obj.from_http_response(response)

    @enable_run_synchronously
    async def get(self, url: str, response_obj: type[T], headers: dict | None = None, **kwargs) -> Awaitable[T] | T:
        if headers is None:
            headers = {}

        if list(self.auth_header.values())[0] is None:
            raise MissingAuthenticationException

        response = await super().get(url, headers={**headers, **self.auth_header}, **kwargs)
        return response_obj.from_http_response(response)

    def put(self, route: str, payload: dict, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        url = self.base_url + route
        if headers is None:
            headers = {}
        response = super().put(url, payload=payload, headers=headers, **kwargs)
        return response

    def delete(self, route: str, params: dict, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        url = self.base_url + route
        if headers is None:
            headers = {}
        response = super().delete(url, params=params, headers=headers, **kwargs)
        return response
