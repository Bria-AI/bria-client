from typing import Any

import httpx
from httpx import Response
from httpx_retries import Retry, RetryTransport

from bria_client.clients.bria_response import BriaResponse
from bria_client.engines.base.base_http_request import BaseHTTPRequest


class SyncHTTPRequest(BaseHTTPRequest):
    """Sync-only HTTP request implementation"""

    def __init__(self, request_timeout: int = 30, retry: Retry | None = None) -> None:
        """
        Initialize the SyncHTTPClient

        Args:
            `request_timeout: int` - The default request timeout for reading response from the server (client side rejection)
            `retry: Retry | None` - Retry configuration for requests
        """
        super().__init__(request_timeout, retry)

        # One sync client for this process:
        self._client = httpx.Client(
            transport=RetryTransport(retry=self._retry) if self._retry is not None else None,
            timeout=self._timeout,
            limits=self._limits,
        )

    def close(self) -> None:
        self._client.close()

    def get(self, url: str, headers: dict[str, str] | None = None, **kwargs: Any) -> BriaResponse:
        response = self._request(url, "GET", headers=headers, **kwargs)
        return BriaResponse.from_http_response(response)  # type: ignore

    def post(self, url: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None, **kwargs: Any) -> BriaResponse:
        response = self._request(url, "POST", payload=payload, headers=headers, **kwargs)
        return BriaResponse.from_http_response(response)  # type: ignore

    def _request(self, url: str, method: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None, **kwargs: Any) -> Response:
        """
        Make a sync http request

        Args:
            `url: str` - The URL to make the request to
            `method: str` - The method to use for the request
            `payload: dict | None` - The payload to send with the request
            `headers: dict | None` - The headers to send with the request
            `**kwargs` - Additional `httpx.request` compatible keyword arguments to pass to the request

        Returns:
            `RT` - The response from the request

        Raises:
            `EngineAPIException` - When the request fails
        """
        response = self._client.request(method, url, headers=headers, json=payload, timeout=self.request_timeout, **kwargs)
        return response
