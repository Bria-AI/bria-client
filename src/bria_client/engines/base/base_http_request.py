from abc import ABC, abstractmethod
from collections.abc import Awaitable
from typing import Any

import httpx
from httpx import Response
from httpx_retries import Retry

from bria_client.clients.bria_response import BriaResponse


class BaseHTTPRequest(ABC):
    """Abstract base class defining the common interface for HTTP requests"""

    def __init__(self, request_timeout: int = 30, retry: Retry | None = None) -> None:
        """
        Initialize the HTTP Client

        Args:
            `request_timeout: int` - The default request timeout for reading response from the server (client side rejection)
            `retry: Retry | None` - Retry configuration for requests
        """
        self.request_timeout = request_timeout
        self._retry = retry
        self._timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)
        self._limits = httpx.Limits(max_keepalive_connections=20, max_connections=100, keepalive_expiry=30.0)

    def get(self, url: str, headers: dict[str, str] | None = None, **kwargs: Any):
        response = self._request(url, "GET", headers=headers, **kwargs)
        return BriaResponse.from_http_response(response)  # type: ignore

    def post(self, url: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None, **kwargs: Any):
        response = self._request(url, "POST", payload=payload, headers=headers, **kwargs)
        return BriaResponse.from_http_response(response)  # type: ignore

    async def get_async(self, url: str, headers: dict[str, str] | None = None, **kwargs: Any):
        response = await self._request(url, "GET", headers=headers, **kwargs)
        return BriaResponse.from_http_response(response)  # type: ignore

    async def post_async(self, url: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None, **kwargs: Any):
        response = await self._request(url, "POST", payload=payload, headers=headers, **kwargs)
        return BriaResponse.from_http_response(response)  # type: ignore

    @abstractmethod
    def _request(
        self, url: str, method: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> Awaitable[Response] | Response:
        """
        Make an http request

        Args:
            `url: str` - The URL to make the request to
            `method: str` - The method to use for the request
            `payload: dict | None` - The payload to send with the request
            `headers: dict | None` - The headers to send with the request
            `**kwargs` - Additional `httpx.request` compatible keyword arguments to pass to the request

        Returns:
            `Awaitable[RT] | RT` - The response from the request
        """
        pass
