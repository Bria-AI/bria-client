import asyncio
from typing import Awaitable, BinaryIO, Tuple
from urllib.parse import urljoin

import httpx

from bria_internal.common.bria_engine_api.constants import BRIA_ENGINE_INTEGRATION_URL, BRIA_ENGINE_PROD_URL
from bria_internal.common.env_config import env_config
from bria_internal.common.singleton_meta import SingletonABCMeta


def running_in_async_context() -> bool:
    """
    Return True if we're already inside a running asyncio event loop.
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


class BriaEngineRequest(metaclass=SingletonABCMeta):
    api_token: str
    jwt_token: str | None
    custom_headers: dict | None

    def __init__(self, api_token: str = None, jwt_token: str | None = None, custom_headers: dict | None = None, custom_base_url: str | None = None) -> None:
        try:
            if api_token is None and env_config.BRIA_ENGINE_API_KEY:
                api_token = env_config.BRIA_ENGINE_API_KEY
        except ValueError:
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

        if env_config.BRIA_ENGINE_URL:
            return str(env_config.BRIA_ENGINE_URL)

        if env_config.IS_PRODUCTION:
            return BRIA_ENGINE_PROD_URL

        return BRIA_ENGINE_INTEGRATION_URL

    def _get_headers(self) -> dict:
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

    async def _async_request(self, method: str, url: str, payload: dict, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            print("requesting asyncly:", url)
            response = await client.request(method, url, headers=self._get_headers(), json=payload, **kwargs)
            response.raise_for_status()
            return response

    def _sync_request(self, method: str, url: str, payload: dict, **kwargs) -> httpx.Response:
        with httpx.Client() as client:
            print("requesting syncly:", url)
            response = client.request(method, url, headers=self._get_headers(), json=payload, **kwargs)
            response.raise_for_status()
            return response

    def get(self, route: str, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "GET", **kwargs)

    def post(self, route: str, payload: dict, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "POST", payload=payload, **kwargs)

    def put(self, route: str, payload: dict, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "PUT", payload=payload, **kwargs)

    def delete(self, route: str, params: dict, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.request(route, "DELETE", params=params, **kwargs)

    def upload(self, route: str, image: str | Tuple[str, Tuple[str, BinaryIO, str]], **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self.post(
            route=route,
            data={"image_url": image} if isinstance(image, str) else {},
            files=[image] if not isinstance(image, str) else None,
            headers=self._get_headers(),
            **kwargs,
        )
