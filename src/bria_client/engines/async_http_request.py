import asyncio
import threading
import weakref
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
        self._retry = retry
        self._timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)
        self._limits = httpx.Limits(max_keepalive_connections=20, max_connections=100, keepalive_expiry=30.0)

        # Saves httpx.AsyncClient instances for each event loop, Using wearkrefDictionary to avoid memory leaks when event loops are garbage collected.
        self._async_clients: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, httpx.AsyncClient] = weakref.WeakKeyDictionary()
        self._async_clients_lock = threading.Lock()  # Lock to prevent race conditions when writing the `_async_clients` dictionary.

        # One sync client for this process:
        self._client = httpx.Client(
            transport=RetryTransport(retry=self._retry) if self._retry is not None else None,
            timeout=self._timeout,
            limits=self._limits,
        )

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
        client: httpx.AsyncClient = self._get_async_client()
        response = await client.request(method, url, headers=headers, json=payload, timeout=self.request_timeout, **kwargs)
        return response

    def _sync_request(self, method: str, url: str, payload: dict | None, headers: dict | None = None, **kwargs) -> httpx.Response:
        response = self._client.request(method, url, headers=headers, json=payload, timeout=self.request_timeout, **kwargs)
        return response

    def _get_async_client(self) -> httpx.AsyncClient:
        """
        Get an async client for the current event loop, create one only if needed.

        Returns:
            `httpx.AsyncClient` - The async client for the current event loop
        """
        loop = asyncio.get_running_loop()

        # Loop key exists → return existing client
        client = self._async_clients.get(loop)
        if client is not None:
            return client

        with self._async_clients_lock:
            client = self._async_clients.get(loop)

            # Dual-check to prevent race conditions, client might have been created by another thread.
            if client is not None:
                return client

            # Otherwise create a new AsyncClient bound to this loop
            client = httpx.AsyncClient(
                timeout=self._timeout,
                limits=self._limits,
            )
            self._async_clients[loop] = client

        return client
