import asyncio
import time
from abc import ABC, abstractmethod
from collections.abc import Awaitable
from urllib.parse import urljoin

import httpx
from httpx_retries import Retry, RetryTransport

from bria_client.decorators.enable_sync_decorator import running_in_async_context
from bria_client.exceptions import EngineAPIException, PollingException, PollingFileStatus


class AsyncHTTPClient(ABC):
    def __init__(self, base_url: str, default_request_timeout: int = 30, retry: Retry | None = None) -> None:
        """
        Initialize the AsyncHTTPClient

        Args:
            `base_url: str` - The base URL to make the request to
            `default_request_timeout: int` - The default request timeout for reading response from the server (client side rejection)
        """
        self.base_url = base_url
        self.default_request_timeout = default_request_timeout
        self.transport = RetryTransport(retry=retry)

    @property
    @abstractmethod
    def headers(self) -> dict:
        pass

    def request(
        self, route: str, method: str, payload: dict | None = None, custom_headers: dict | None = None, **kwargs
    ) -> Awaitable[httpx.Response] | httpx.Response:
        """
        Make an http request using Bria Engine Client

        Args:
            `route: str` - The route to make the request to
            `method: str` - The method to use for the request
            `payload: dict | None` - The payload to send with the request
            `custom_headers: dict | None` - The custom headers to send with the request

            `**kwargs` - Additional `httpx.request` compatible keyword arguments to pass to the request

        Returns:
            `Awaitable[httpx.Response] | httpx.Response` - The response from the request

        Raises:
            `EngineAPIException` - When the request fails
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
        async with httpx.AsyncClient(transport=self.transport) as client:
            try:
                response = await client.request(method, url, headers=headers, json=payload, timeout=self.default_request_timeout, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                raise EngineAPIException(url=url, base_url=self.base_url, http_status_error=e)

    def _sync_request(self, method: str, url: str, payload: dict | None, headers: dict | None = None, **kwargs) -> httpx.Response:
        with httpx.Client(transport=self.transport) as client:
            try:
                response = client.request(method, url, headers=headers, json=payload, timeout=self.default_request_timeout, **kwargs)
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

    def _check_polling_status(self, response: httpx.Response) -> bool:
        if response.status_code in (200, 206):
            content_length = int(response.headers.get("Content-Length", 0))
            if content_length > 0:
                return True
            else:
                raise PollingException(PollingFileStatus.ZERO_BYTE_IMAGE_ERROR)
        elif response.status_code == 416:
            raise PollingException(PollingFileStatus.ZERO_BYTE_IMAGE_ERROR)
        else:
            return False

    async def _async_file_polling(self, file_url: str, headers: dict, timeout: int = 120, interval: int = 2) -> Awaitable[None]:
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", file_url, timeout=self.default_request_timeout, headers=headers) as response:
                    if self._check_polling_status(response):
                        return

            await asyncio.sleep(interval)

        raise PollingException(PollingFileStatus.TIMEOUT_ERROR)

    def _sync_file_polling(self, file_url: str, headers: dict, timeout: int = 120, interval: int = 2) -> None:
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            with httpx.Client() as client:
                with client.stream("GET", file_url, timeout=self.default_request_timeout, headers=headers) as response:
                    if self._check_polling_status(response):
                        return

            time.sleep(interval)

        raise PollingException(PollingFileStatus.TIMEOUT_ERROR)

    def file_polling(self, file_url: str, timeout: int = 120, interval: int = 2) -> Awaitable[None] | None:
        """
        Polling the file from the file URL until the file is ready

        Args:
            `file_url: str` - The URL of the file to poll
            `timeout: int` - The timeout in seconds
            `interval: int` - The interval in seconds

        Raises:
            `PollingException[Timeout]` - If the file is not accessible after the timeout

            `PollingException[ZeroByteImage]` - If the file is a zero byte image
        """
        headers: dict = {"Range": "bytes=0-0"}
        if running_in_async_context():
            return self._async_file_polling(file_url, headers, timeout, interval)
        else:
            return self._sync_file_polling(file_url, headers, timeout, interval)
