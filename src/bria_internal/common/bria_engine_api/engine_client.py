from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import Awaitable
from urllib.parse import urljoin

import httpx

from bria_internal.common.bria_engine_api.constants import BRIA_ENGINE_INTEGRATION_URL, BRIA_ENGINE_PRODUCTION_URL
from bria_internal.common.bria_engine_api.enable_sync_decorator import running_in_async_context
from bria_internal.common.settings import engine_settings
from bria_internal.exceptions.engine_api_exception import EngineAPIException


class AsyncHTTPClient(ABC):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    @property
    @abstractmethod
    def headers(self) -> dict:
        pass

    def request(
        self, route: str, method: str, payload: dict | None = None, custom_headers: dict | None = None, **kwargs
    ) -> Awaitable[httpx.Response] | httpx.Response:
        """
        Make a request using Bria Engine Client

        Args:
            route: str - The route to make the request to
            method: str - The method to use for the request
            payload: dict | None - The payload to send with the request
            custom_headers: dict | None - The custom headers to send with the request
            **kwargs: dict - Additional keyword arguments to pass to the request

        Returns:
            Awaitable[httpx.Response] | httpx.Response - The response from the request

        Raises:
            EngineAPIException: When the request fails
        """
        route = urljoin(self.base_url, route)
        headers: dict = self._merge_headers(custom_headers)

        if running_in_async_context():
            return self._async_request(method, route, payload, headers=headers, **kwargs)
        else:
            return self._sync_request(method, route, payload, headers=headers, **kwargs)

    def _merge_headers(self, custom_headers: dict | None = None) -> dict:
        headers: dict = self.headers
        if custom_headers:
            headers.update(custom_headers)
        return headers

    async def _async_request(self, method: str, url: str, payload: dict | None, headers: dict | None = None, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, headers=headers, json=payload, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                raise EngineAPIException(url=url, base_url=self.base_url, http_status_error=e)

    def _sync_request(self, method: str, url: str, payload: dict | None, headers: dict | None = None, **kwargs) -> httpx.Response:
        with httpx.Client() as client:
            try:
                response = client.request(method, url, headers=headers, json=payload, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                raise EngineAPIException(url=url, base_url=self.base_url, http_status_error=e)

    def get(self, route: str, custom_headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "GET", custom_headers=custom_headers, **kwargs)

    def post(self, route: str, payload: dict, custom_headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "POST", payload=payload, custom_headers=custom_headers, **kwargs)

    def put(self, route: str, payload: dict, custom_headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "PUT", payload=payload, custom_headers=custom_headers, **kwargs)

    def delete(self, route: str, url_params: dict, custom_headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "DELETE", params=url_params, custom_headers=custom_headers, **kwargs)


class BriaEngineClient(AsyncHTTPClient):
    def __init__(self, api_token_ctx: ContextVar[str] | None = None, jwt_token_ctx: ContextVar[str] | None = None) -> None:
        if api_token_ctx is None and engine_settings.API_KEY:
            api_token_ctx = ContextVar("bria_engine_api_token", default=engine_settings.API_KEY)
        elif api_token_ctx is None and jwt_token_ctx is None:
            raise ValueError("Bria Engine API key in not provided and JWT token is not provided")

        self.api_token_ctx = api_token_ctx
        self.jwt_token_ctx = jwt_token_ctx

        super().__init__(base_url=str(engine_settings.URL) or self._get_env_based_url())

    def _get_env_based_url(self) -> str:
        if engine_settings.IS_PRODUCTION:
            return BRIA_ENGINE_PRODUCTION_URL
        return BRIA_ENGINE_INTEGRATION_URL

    @property
    def headers(self) -> dict:
        headers: dict = {"api_token": self.api_token} if self.api_token else {"jwt": self.jwt_token}
        return headers

    @property
    def api_token(self) -> str:
        try:
            return self.api_token_ctx.get()
        except LookupError:
            raise ValueError("API token is not set")

    @property
    def jwt_token(self) -> str | None:
        try:
            if self.jwt_token_ctx is None:
                return None

            return self.jwt_token_ctx.get()
        except LookupError:
            # ContextVar not exists but not initialized yet
            return None
