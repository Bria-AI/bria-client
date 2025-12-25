from abc import ABC
from collections.abc import Awaitable

import httpx
from httpx_retries import Retry, RetryTransport

from bria_client.decorators.enable_sync_decorator import running_in_async_context


class AsyncHTTPRequest(ABC):
    def __init__(self, request_timeout: int = 30, retry: Retry | None = None) -> None:
        """
        Initialize the AsyncHTTPClient

        Args:
            `base_url: str` - The base URL to make the request to
            `request_timeout: int` - The default request timeout for reading response from the server (client side rejection)
        """
        self.request_timeout = request_timeout
        self.retry = retry

    def get(self, url: str, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        response = self._request(url, "GET", headers=headers, **kwargs)
        return response

    def post(self, url: str, payload: dict, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self._request(url, "POST", payload=payload, headers=headers, **kwargs)

    def put(self, url: str, payload: dict, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self._request(url, "PUT", payload=payload, headers=headers, **kwargs)

    def delete(self, url: str, params: dict, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self._request(url, "DELETE", params=params, headers=headers, **kwargs)

    def _request(self, url: str, method: str, payload: dict | None = None, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        """
        Make an http request using Bria Engine Client

        Args:
            `route: str` - The route to make the request to
            `method: str` - The method to use for the request
            `payload: dict | None` - The payload to send with the request
            `headers: dict | None` - The headers to send with the request

            `**kwargs` - Additional `httpx.request` compatible keyword arguments to pass to the request

        Returns:
            `Awaitable[httpx.Response] | httpx.Response` - The response from the request

        Raises:
            `EngineAPIException` - When the request fails
        """

        if running_in_async_context():
            return self._async_request(method, url, payload, headers=headers, **kwargs)
        return self._sync_request(method, url, payload, headers=headers, **kwargs)

    async def _async_request(self, method: str, url: str, payload: dict | None, headers: dict | None = None, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(transport=RetryTransport(retry=self.retry)) as client:
            response = await client.request(method, url, headers=headers, json=payload, timeout=self.request_timeout, **kwargs)
            return response

    def _sync_request(self, method: str, url: str, payload: dict | None, headers: dict | None = None, **kwargs) -> httpx.Response:
        with httpx.Client(transport=RetryTransport(retry=self.retry)) as client:
            response = client.request(method, url, headers=headers, json=payload, timeout=self.request_timeout, **kwargs)
            return response
