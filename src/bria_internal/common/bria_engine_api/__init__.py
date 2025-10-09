import asyncio
from typing import Awaitable, BinaryIO, Tuple
from urllib.parse import urljoin

import httpx

from bria_internal.common.bria_engine_api.constants import BRIA_ENGINE_INTEGRATION_URL, BRIA_ENGINE_PROD_URL
from bria_internal.common.settings import engine_settings


def running_in_async_context() -> bool:
    """
    Return True if we're already inside a running asyncio event loop.
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


class BriaEngineRequest:
    api_token: str
    jwt_token: str | None
    custom_headers: dict | None

    def __init__(self, api_token: str = None, jwt_token: str | None = None, custom_headers: dict | None = None, custom_base_url: str | None = None) -> None:
        if api_token is None and engine_settings.API_KEY:
            api_token = engine_settings.API_KEY
        elif api_token is None:
            raise ValueError("Bria Engine API key in not provided")

        self.api_token = api_token
        self.jwt_token = jwt_token
        self.custom_headers = custom_headers
        self.base_url = self._get_bria_engine_base_url(custom_base_url)

    def _get_bria_engine_base_url(self, custom_base_url: str | None = None) -> str:
        """
        Determine the Bria Engine base URL based on configuration.

        Priority order:
        1. Custom base URL (if provided)
        2. Environment variable BRIA_ENGINE_URL
        3. Production URL (if IS_PRODUCTION is True)
        4. Integration URL (default)

        Args:
                custom_base_url: Optional custom base URL to use

        Returns:
            The determined base URL
        """
        if custom_base_url is not None:
            return custom_base_url

        if engine_settings.URL:
            return str(engine_settings.URL)

        if engine_settings.IS_PRODUCTION:
            return BRIA_ENGINE_PROD_URL

        return BRIA_ENGINE_INTEGRATION_URL

    def _get_headers(self) -> dict:
        if not self.api_token and not self.jwt_token:
            raise ValueError("Bria Engine API key in not provided")

        headers = {"api_token": self.api_token} if self.api_token else {"jwt": self.jwt_token}
        if self.custom_headers:
            headers.update(self.custom_headers)
        return headers

    def request(self, route: str, method: str, payload: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        route = urljoin(self.base_url, route)

        if running_in_async_context():
            return self._async_request(method, route, payload, **kwargs)
        else:
            return self._sync_request(method, route, payload, **kwargs)

    async def _async_request(self, method: str, url: str, payload: dict | None, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=self._get_headers(), json=payload, **kwargs)
            response.raise_for_status()
            return response

    def _sync_request(self, method: str, url: str, payload: dict | None, **kwargs) -> httpx.Response:
        with httpx.Client() as client:
            response = client.request(method, url, headers=self._get_headers(), json=payload, **kwargs)
            response.raise_for_status()
            return response

    def get(self, route: str, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "GET", **kwargs)

    def post(self, route: str, payload: dict, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "POST", payload=payload, **kwargs)

    def put(self, route: str, payload: dict, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "PUT", payload=payload, **kwargs)

    def delete(self, route: str, url_params: dict, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "DELETE", params=url_params, **kwargs)

    def upload(self, route: str, image: str | Tuple[str, Tuple[str, BinaryIO, str]], **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.post(
            route=route,
            data={"image_url": image} if isinstance(image, str) else {},
            files=[image] if not isinstance(image, str) else None,
            headers=self._get_headers(),
            **kwargs,
        )
