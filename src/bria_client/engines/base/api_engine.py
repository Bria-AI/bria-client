import os
from abc import abstractmethod
from collections.abc import Awaitable
from typing import Any, NoReturn, TypeVar

import httpx
from httpx_retries import Retry

from bria_client.constants import BRIA_ENGINE_PRODUCTION_URL
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.engines.base.async_http_request import AsyncHTTPRequest
from bria_client.exceptions.bria_exception import BriaException
from bria_client.exceptions.old.engine_api_exception import EngineAPIException
from bria_client.responses import BriaResponse
from bria_client.schemas.base_models import BriaPayload

T = TypeVar("T", bound=BriaResponse)


class ApiEngine(AsyncHTTPRequest):
    """this should be the abstract base class for all engines"""

    def __init__(self, auth_header: dict, base_url: str | None = None, retry: Retry | None = Retry(total=3, backoff_factor=2)):
        if base_url is None:
            base_url = os.environ.get("BRIA_ENGINE_BASE_URL", BRIA_ENGINE_PRODUCTION_URL)
        self.base_url = base_url
        self.retry = retry
        self.auth_header = auth_header
        super().__init__(retry=retry)

    @enable_run_synchronously
    async def post(self, url: str, payload: BriaPayload, response_obj: type[T], headers: dict | None = None, **kwargs) -> Awaitable[T] | T:
        if headers is None:
            headers = {}

        if list(self.auth_header.values())[0] is None:
            raise BriaException(message="No authentication found for request...")

        response = await super().post(url, payload=payload.model_dump(exclude_none=True), headers={**headers, **self.auth_header}, **kwargs)
        return response_obj.from_http_response(response)

    @enable_run_synchronously
    async def get(self, url: str, response_obj: type[T], headers: dict | None = None, **kwargs) -> Awaitable[T] | T:
        if headers is None:
            headers = {}
        response = await super().get(url, headers={**headers, **self.auth_header}, **kwargs)
        return response_obj.from_http_response(response)

    def put(self, route: str, payload: dict, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        url = self.base_url + route
        try:
            response = self.put(url, payload=payload, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except EngineAPIException as e:
            return self.custom_exception_handle(e)

    def delete(self, route: str, params: dict, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        url = self.base_url + route
        try:
            response = self.delete(url, params=params, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except EngineAPIException as e:
            return self.custom_exception_handle(e)

    @abstractmethod
    def custom_exception_handle(self, e: EngineAPIException, payload: BriaPayload | None = None) -> Any | NoReturn:
        raise e
