import asyncio
import logging
import time

from httpx_retries import Retry

from bria_client.clients.base import BaseBriaClient
from bria_client.engines.base import AsyncHTTPRequest
from bria_client.toolkit import BriaResponse
from bria_client.toolkit.models import Status

logger = logging.getLogger(__name__)


class BriaAsyncClient(BaseBriaClient):
    """Asynchronous Bria API client"""

    def _setup_http_client(self, retry: Retry | None) -> None:
        """Set up the asynchronous HTTP client"""
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
            await self.engine.client.close()

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
