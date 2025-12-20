import os
from abc import abstractmethod
from collections.abc import Awaitable
from typing import Any, NoReturn, TypeVar

import httpx
from httpx_retries import Retry

from bria_client.constants import BRIA_ENGINE_PRODUCTION_URL
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.engines.base.async_http_request import AsyncHTTPRequest
from bria_client.exceptions.old.engine_api_exception import EngineAPIException
from bria_client.responses import BriaResponse
from bria_client.schemas.base_models import APIPayloadModel

T = TypeVar("T", bound=BriaResponse)


class ApiEngine(AsyncHTTPRequest):
    """this should be the abstract base class for all engines"""

    def __init__(self, base_url: str | None = None, retry: Retry | None = Retry(total=3, backoff_factor=2)):
        if base_url is None:
            base_url = os.environ.get("BRIA_ENGINE_BASE_URL", BRIA_ENGINE_PRODUCTION_URL)
        self.base_url = base_url
        self.retry = retry
        super().__init__(retry=retry)

    def post(self, route: str, payload: dict, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        url = self.base_url + route
        response = self.post(url, payload=payload, headers=headers, **kwargs)
        return response

    @enable_run_synchronously
    async def get(self, route: str, response_obj: type[T], headers: dict | None = None, **kwargs) -> Awaitable[T] | T:
        url = self.base_url + route
        response = await super().get(url, headers=headers, **kwargs)
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
    def custom_exception_handle(self, e: EngineAPIException, payload: APIPayloadModel | None = None) -> Any | NoReturn:
        raise e
