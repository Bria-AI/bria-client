from collections.abc import Callable
from typing import Any, TypeVar

from httpx_retries import Retry

from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.engines.async_http_request import AsyncHTTPRequest
from bria_client.exceptions import MissingAuthenticationException
from bria_client.payloads.bria_payload import BriaPayload
from bria_client.results import BriaResponse, BriaResult

T = TypeVar("T", bound=BriaResult)


class ApiEngine(AsyncHTTPRequest[Any]):
    """this should be the abstract base class for all engines"""

    def __init__(self, default_headers: dict | Callable[[], dict], base_url: str, retry: Retry | None = None):
        if retry is None:
            retry = Retry(total=3, backoff_factor=2)
        self.base_url = base_url
        self.retry = retry
        self._default_headers = default_headers
        super().__init__(retry=retry)

    @property
    def default_headers(self) -> dict[str, str]:
        if isinstance(self._default_headers, Callable):
            return self._default_headers()
        return self._default_headers

    @enable_run_synchronously
    async def post(
        self,
        url: str,
        payload: BriaPayload,
        result_obj: type[T],
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> BriaResponse[T]:
        if headers is None:
            headers = {}
        if list(self.default_headers.values())[0] is None:
            raise MissingAuthenticationException
        response = await self._post(url, payload=payload.model_dump(mode="json"), headers={**headers, **self.default_headers}, **kwargs)
        return BriaResponse[result_obj].from_http_response(response)  # type: ignore

    @enable_run_synchronously
    async def get(
        self,
        url: str,
        result_obj: type[T],
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> BriaResponse[T]:
        if headers is None:
            headers = {}

        if list(self.default_headers.values())[0] is None:
            raise MissingAuthenticationException

        response = await self._get(url, headers={**headers, **self.default_headers}, **kwargs)

        return BriaResponse[result_obj].from_http_response(response)  # type: ignore
