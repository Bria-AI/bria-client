import logging
import time
from pathlib import Path

import httpx
from httpx_retries import Retry

from bria_client.clients.base import BaseBriaClient
from bria_client.engines.base.sync_http_request import SyncHTTPRequest
from bria_client.toolkit import BriaResponse
from bria_client.toolkit.errors.exception import BriaException

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

    def submit(self, endpoint: str, payload: dict, headers: dict | None = None, raise_for_status: bool = False, webhook_url: str | None = None, **kwargs):
        """
        Submit an asynchronous request (sync=False)

        Args:
            endpoint: API endpoint to call
            payload: Request payload
            headers: Optional headers
            raise_for_status: Whether to raise exception on error status
            webhook_url: Optional URL to receive a POST when the job reaches a terminal state.
                         Bria will sign the request with HMAC-SHA256; use
                         ``verify_webhook_signature`` from ``bria_client.toolkit`` to verify on receipt.
            **kwargs: Additional arguments (e.g., api_token)

        Returns:
            BriaResponse: The API response with request_id for polling
        """
        self._validate_submit_payload(payload)
        merged_payload = {**payload, "sync": False}
        if webhook_url is not None:
            merged_payload["webhook_url"] = webhook_url
        bria_response = self.engine.post(endpoint=endpoint, payload=merged_payload, headers={**(headers or {})}, **kwargs)
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

    def upload(self, path: str | Path, media_type: str | None = None, headers: dict | None = None, **kwargs) -> str:
        """
        Upload a local file to Bria's storage and return a URL ready for use in API calls.

        Args:
            path: Local path to the file.
            media_type: MIME type of the file (e.g. "video/mp4"). If omitted, any "video/*" type is accepted.
            headers: Optional headers for the Bria API call.
            **kwargs: Additional arguments forwarded to the Bria API call (e.g., api_token).

        Returns:
            str: The file_url to use as input in subsequent Bria API calls.
                 Valid for 1 day; keep it safe as anyone with the URL can access the file.

        Raises:
            NotImplementedError: If the media type is not yet supported.
            ValueError: If the upload fails.
        """
        if media_type is not None and not media_type.startswith("video/"):
            raise NotImplementedError(f"Upload not yet supported for media type: {media_type!r}")
        bria_response = self.engine.post(
            endpoint="video/upload",
            payload={"media_type": media_type},
            headers={**(headers or {})},
            **kwargs,
        )
        bria_response.raise_for_status()
        result = bria_response.result
        assert result is not None
        path = Path(path)
        with path.open("rb") as f:
            with httpx.Client() as client:
                response = client.post(
                    result.upload_url,
                    data=result.upload_fields,
                    files={"file": (path.name, f, media_type)},
                    timeout=None,
                )
        if response.status_code != 204:
            raise BriaException(status_code=response.status_code, message="Upload failed", details=response.text)
        return result.file_url

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
