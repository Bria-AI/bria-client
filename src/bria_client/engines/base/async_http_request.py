import asyncio
import threading
import weakref
from collections.abc import Awaitable
from typing import Any

import httpx
from httpx_retries import Retry

from bria_client.engines.base.base_http_request import RT, BaseHTTPRequest


class AsyncHTTPRequest(BaseHTTPRequest[RT]):
    """Async-only HTTP request implementation"""

    def __init__(self, request_timeout: int = 30, retry: Retry | None = None) -> None:
        """
        Initialize the AsyncHTTPClient

        Args:
            `request_timeout: int` - The default request timeout for reading response from the server (client side rejection)
            `retry: Retry | None` - Retry configuration for requests
        """
        super().__init__(request_timeout, retry)

        # Saves httpx.AsyncClient instances for each event loop, Using weakrefDictionary to avoid memory leaks when event loops are garbage collected.
        self._async_clients: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, httpx.AsyncClient] = weakref.WeakKeyDictionary()
        self._async_clients_lock = threading.Lock()  # Lock to prevent race conditions when writing the `_async_clients` dictionary.

    def _request(self, url: str, method: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None, **kwargs: Any) -> Awaitable[RT]:
        """
        Make an async http request

        Args:
            `url: str` - The URL to make the request to
            `method: str` - The method to use for the request
            `payload: dict | None` - The payload to send with the request
            `headers: dict | None` - The headers to send with the request
            `**kwargs` - Additional `httpx.request` compatible keyword arguments to pass to the request

        Returns:
            `Awaitable[RT]` - The response from the request

        Raises:
            `EngineAPIException` - When the request fails
        """
        return self._async_request(method, url, payload, headers=headers, **kwargs)  # type: ignore

    async def _async_request(
        self, method: str, url: str, payload: dict[str, Any] | None, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> httpx.Response:
        client: httpx.AsyncClient = self._get_async_client()
        response = await client.request(method, url, headers=headers, json=payload, timeout=self.request_timeout, **kwargs)
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
