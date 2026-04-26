import logging
import time

from httpx_retries import Retry

from bria_client.clients.base import BaseBriaClient
from bria_client.engines.base.sync_http_request import SyncHTTPRequest
from bria_client.toolkit import BriaResponse

logger = logging.getLogger(__name__)


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
        # Unpack payload and headers to avoid mutating the original input
        bria_response = self.engine.post(endpoint=endpoint, payload={**payload, "sync": True}, headers={**(headers or {})}, **kwargs)
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
        # Unpack payload and headers to avoid mutating the original input
        bria_response = self.engine.post(endpoint=endpoint, payload={**payload, "sync": False}, headers={**(headers or {})}, **kwargs)
        if raise_for_status:
            bria_response.raise_for_status()
        return bria_response

    def get(self, endpoint: str, params: dict | None = None, headers: dict | None = None, raise_for_status: bool = False, **kwargs):
        """
        Perform an HTTP GET request against an API endpoint.

        Args:
            endpoint: API endpoint to call.
            params: Optional query string parameters.
            headers: Optional headers. Not mutated.
            raise_for_status: Whether to raise an exception on error status.
            **kwargs: Additional arguments forwarded to the HTTP layer (e.g., ``api_token``).

        Returns:
            BriaResponse: The API response.
        """
        # Unpack headers and params to avoid mutating the original inputs
        bria_response = self.engine.get(endpoint=endpoint, headers={**(headers or {})}, params={**(params or {})}, **kwargs)
        if raise_for_status:
            bria_response.raise_for_status()
        return bria_response

    def status(self, request_id: str, headers: dict | None = None, **kwargs):
        bria_response = self.engine.get(endpoint=f"status/{request_id}", headers=headers, **kwargs)
        return bria_response.status

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

        headers = {**(headers or {})}

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
