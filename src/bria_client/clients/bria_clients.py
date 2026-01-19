import asyncio
import logging
import time
import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import overload

from httpx_retries import Retry

from bria_client.clients.bria_response import BriaResponse
from bria_client.engines.api_engine import ApiEngine
from bria_client.engines.base.async_http_request import AsyncHTTPRequest
from bria_client.engines.base.sync_http_request import SyncHTTPRequest
from bria_client.engines.bria_engine import BriaEngine
from bria_client.toolkit.status import Status

logger = logging.getLogger(__name__)


class BaseBriaClient(ABC):
    """Abstract base class for Bria clients"""

    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | Callable[[], str] | None = None,
        retry: Retry | None = None,
        *,
        api_engine: ApiEngine | None = None,
    ):
        if (base_url is not None or api_token is not None) and api_engine is not None:
            warnings.warn("ApiEngine is provided..., Other input parameters will be ignored")

        self.engine = api_engine or BriaEngine(base_url=base_url.rstrip("/") if base_url else None, api_token=api_token)
        self._setup_http_client(retry or Retry(total=3, backoff_factor=2))

    @abstractmethod
    def _setup_http_client(self, retry: Retry | None) -> None:
        """Setup the HTTP client for this client instance"""
        pass

    def _validate_run_payload(self, payload: dict) -> None:
        """Validate payload for run() method"""
        assert "sync" not in payload, ".run() always runs in sync=True (to use async call .submit())"

    def _validate_submit_payload(self, payload: dict) -> None:
        """Validate payload for submit() method"""
        assert "sync" not in payload, ".submit() always runs in sync=False (to use sync call .run())"

    def _extract_request_id(self, target: str | BriaResponse | None, response: BriaResponse | None = None, request_id: str | None = None) -> str:
        """Extract request_id from various input formats"""
        extracted_id = request_id
        if response is not None:
            extracted_id = response.request_id
        if target is not None:
            extracted_id = target.request_id if isinstance(target, BriaResponse) else target
        if extracted_id is None:
            raise ValueError("request_id is required")
        return extracted_id


class BriaSyncClient(BaseBriaClient):
    """Synchronous Bria API client"""

    def __enter__(self):
        """Async context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.close()

    def close(self) -> None:
        """Close the async HTTP client"""
        if isinstance(self.engine.client, SyncHTTPRequest):
            self.engine.client.close()

    def _setup_http_client(self, retry: Retry | None) -> None:
        """Setup synchronous HTTP client"""
        self.engine.set_http_client(http_client=SyncHTTPRequest(retry=retry))

    def run(self, endpoint: str, payload: dict, headers: dict | None = None, raise_for_status: bool = False, **kwargs):
        """
        Run a synchronous request (sync=True)

        Args:
            endpoint: API endpoint to call
            payload: Request payload
            headers: Optional headers
            raise_for_status: Whether to raise exception on error status
            **kwargs: Additional arguments (e.g., api_token)

        Returns:
            BriaResponse: The API response
        """
        self._validate_run_payload(payload)
        payload["sync"] = True
        bria_response = self.engine.post(endpoint=endpoint, payload=payload, headers=headers, **kwargs)
        if raise_for_status:
            bria_response.raise_for_status()
        return bria_response

    def submit(self, endpoint: str, payload: dict, headers: dict | None = None, raise_for_status: bool = False, **kwargs):
        """
        Submit an asynchronous request (sync=False)

        Args:
            endpoint: API endpoint to call
            payload: Request payload
            headers: Optional headers
            raise_for_status: Whether to raise exception on error status
            **kwargs: Additional arguments (e.g., api_token)

        Returns:
            BriaResponse: The API response with request_id for polling
        """
        self._validate_submit_payload(payload)
        payload["sync"] = False

        bria_response = self.engine.post(endpoint=endpoint, payload=payload, headers=headers, **kwargs)
        if raise_for_status:
            bria_response.raise_for_status()
        return bria_response

    def status(self, request_id: str, headers: dict | None = None, **kwargs):
        bria_response = self.engine.get(endpoint=f"status/{request_id}", headers=headers, **kwargs)
        return bria_response.status

    @overload
    def poll(
        self, target: BriaResponse, headers: dict | None = None, interval: int | float = 1, timeout: int = 60, raise_for_status: bool = True, **kwargs
    ): ...

    @overload
    def poll(self, target: str, headers: dict | None = None, interval: int | float = 1, timeout: int = 60, raise_for_status: bool = True, **kwargs): ...

    def poll(
        self,
        target: str | BriaResponse | None = None,
        headers: dict | None = None,
        interval: int | float = 1,
        timeout: int = 60,
        raise_for_status: bool = True,
        *,
        response: BriaResponse | None = None,
        request_id: str | None = None,
        **kwargs,
    ):
        request_id = request_id
        if response is not None:
            request_id = response.request_id
        if target is not None:
            request_id = target.request_id if isinstance(target, BriaResponse) else target

        if headers is None:
            headers = {}

        def call_status_service():
            return self.engine.get(endpoint=f"status/{request_id}", headers=headers, **kwargs)

        bria_response = call_status_service()
        start_time = time.time()
        while bria_response.in_progress:
            logger.debug(f"Polling request ID: {request_id}, current status: {bria_response.status}")
            time.sleep(interval)
            bria_response = call_status_service()
            if time.time() - start_time >= timeout:
                raise TimeoutError("Timeout reached while waiting for status request")

        if raise_for_status:
            bria_response.raise_for_status()
        return bria_response


class BriaAsyncClient(BaseBriaClient):
    """Asynchronous Bria API client"""

    def _setup_http_client(self, retry: Retry | None) -> None:
        """Setup asynchronous HTTP client"""
        self.engine.set_http_client(http_client=AsyncHTTPRequest(retry=retry))

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the async HTTP client"""
        if isinstance(self.engine.client, AsyncHTTPRequest):
            await self.engine.client.aclose()

    async def run(self, endpoint: str, payload: dict, headers: dict | None = None, raise_for_status: bool = False, **kwargs):
        """
        Run a synchronous request (sync=True) asynchronously

        Args:
            endpoint: API endpoint to call
            payload: Request payload
            headers: Optional headers
            raise_for_status: Whether to raise exception on error status
            **kwargs: Additional arguments (e.g., api_token)

        Returns:
            BriaResponse: The API response
        """
        self._validate_run_payload(payload)
        payload["sync"] = True
        bria_response = await self.engine.post_async(endpoint=endpoint, payload=payload, headers=headers, **kwargs)
        if raise_for_status:
            bria_response.raise_for_status()
        return bria_response

    async def submit(self, endpoint: str, payload: dict, headers: dict | None = None, raise_for_status: bool = False, **kwargs):
        """
        Submit an asynchronous request (sync=False)

        Args:
            endpoint: API endpoint to call
            payload: Request payload
            headers: Optional headers
            raise_for_status: Whether to raise exception on error status
            **kwargs: Additional arguments (e.g., api_token)

        Returns:
            BriaResponse: The API response with request_id for polling
        """
        self._validate_submit_payload(payload)
        payload["sync"] = False

        bria_response = await self.engine.post_async(endpoint=endpoint, payload=payload, headers=headers, **kwargs)
        if raise_for_status:
            bria_response.raise_for_status()
        return bria_response

    async def status(self, request_id: str, headers: dict | None = None, **kwargs):
        """
        Get the status of a request

        Args:
            request_id: The request ID to check status for
            headers: Optional headers
            **kwargs: Additional arguments (e.g., api_token)

        Returns:
            Status: The current status of the request
        """
        bria_response = await self.engine.get_async(endpoint=f"status/{request_id}", headers=headers, **kwargs)
        return bria_response.status

    @overload
    async def poll(
        self, target: BriaResponse, headers: dict | None = None, interval: int | float = 1, timeout: int = 60, raise_for_status: bool = True, **kwargs
    ): ...

    @overload
    async def poll(self, target: str, headers: dict | None = None, interval: int | float = 1, timeout: int = 60, raise_for_status: bool = True, **kwargs): ...

    async def poll(
        self,
        target: str | BriaResponse | None = None,
        headers: dict | None = None,
        interval: int | float = 1,
        timeout: int = 60,
        raise_for_status: bool = True,
        *,
        response: BriaResponse | None = None,
        request_id: str | None = None,
        **kwargs,
    ):
        """
        Poll for request completion

        Args:
            target: Request ID string or BriaResponse object
            headers: Optional headers
            interval: Polling interval in seconds
            timeout: Timeout in seconds
            raise_for_status: Whether to raise exception on error status
            response: Alternative way to pass BriaResponse (keyword-only)
            request_id: Alternative way to pass request_id (keyword-only)
            **kwargs: Additional arguments (e.g., api_token)

        Returns:
            BriaResponse: The final response after completion

        Raises:
            TimeoutError: If timeout is reached before completion
        """
        extracted_id = self._extract_request_id(target, response, request_id)

        if headers is None:
            headers = {}

        async def call_status_service():
            return await self.engine.get_async(endpoint=f"status/{extracted_id}", headers=headers, **kwargs)

        bria_response = await call_status_service()
        start_time = time.time()
        while bria_response.in_progress or bria_response.status == Status.UNKNOWN:
            logger.debug(f"Polling request ID: {extracted_id}, current status: {bria_response.status}")
            await asyncio.sleep(interval)
            bria_response = await call_status_service()
            if time.time() - start_time >= timeout:
                raise TimeoutError("Timeout reached while waiting for status request")

        if raise_for_status:
            bria_response.raise_for_status()
        return bria_response
