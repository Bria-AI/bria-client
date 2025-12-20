import asyncio
import time
from abc import ABC
from collections.abc import Awaitable

import httpx
from httpx_retries import Retry, RetryTransport

from bria_client.decorators.enable_sync_decorator import running_in_async_context
from bria_client.exceptions import EngineAPIException, PollingException, PollingFileStatus


class AsyncHTTPRequest(ABC):
    def __init__(self, request_timeout: int = 30, retry: Retry | None = None) -> None:
        """
        Initialize the AsyncHTTPClient

        Args:
            `base_url: str` - The base URL to make the request to
            `request_timeout: int` - The default request timeout for reading response from the server (client side rejection)
        """
        self.request_timeout = request_timeout
        self.transport = RetryTransport(retry=retry)

    def get(self, url: str, headers: dict | None = None, **kwargs) -> Awaitable[httpx.Response] | httpx.Response:
        return self._request(url, "GET", headers=headers, **kwargs)

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
        async with httpx.AsyncClient(transport=self.transport) as client:
            try:
                response = await client.request(method, url, headers=headers, json=payload, timeout=self.request_timeout, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                raise EngineAPIException(url=url, http_status_error=e)

    def _sync_request(self, method: str, url: str, payload: dict | None, headers: dict | None = None, **kwargs) -> httpx.Response:
        with httpx.Client(transport=self.transport) as client:
            try:
                response = client.request(method, url, headers=headers, json=payload, timeout=self.request_timeout, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                raise EngineAPIException(url=url, http_status_error=e)

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

    async def _async_file_polling(self, file_url: str, headers: dict, timeout: int = 120, interval: int = 2) -> None:
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", file_url, timeout=self.request_timeout, headers=headers) as response:
                    if self._check_polling_status(response):
                        return

            await asyncio.sleep(interval)

        raise PollingException(PollingFileStatus.TIMEOUT_ERROR)

    def _sync_file_polling(self, file_url: str, headers: dict, timeout: int = 120, interval: int = 2) -> None:
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            with httpx.Client() as client:
                with client.stream("GET", file_url, timeout=self.request_timeout, headers=headers) as response:
                    if self._check_polling_status(response):
                        return

            time.sleep(interval)

        raise PollingException(PollingFileStatus.TIMEOUT_ERROR)

    # TODO: remove this method from here as it is not related to this client
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
        return self._sync_file_polling(file_url, headers, timeout, interval)
