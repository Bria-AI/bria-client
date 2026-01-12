import logging
import time
import warnings
from collections.abc import Callable
from typing import overload

from httpx_retries import Retry

from bria_client.clients.bria_response import BriaResponse
from bria_client.engines.api_engine import ApiEngine
from bria_client.engines.base.sync_http_request import SyncHTTPRequest
from bria_client.engines.bria_engine import BriaEngine
from bria_client.toolkit.status import Status

logger = logging.getLogger(__name__)


class BriaSyncClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | Callable[[], str] | None = None,
        retry: Retry | None = Retry(total=3, backoff_factor=2),
        api_engine: ApiEngine | None = None,
    ):
        if (base_url is not None or api_token is not None) and api_engine is not None:
            warnings.warn("ApiEngine is provided..., Other input parameters will be ignored")

        self.engine = api_engine or BriaEngine(base_url=base_url.rstrip("/"), api_token=api_token)
        self.engine.set_http_client(http_client=SyncHTTPRequest(retry=retry))

    def run(self, endpoint: str, payload: dict, headers: dict | None = None, raise_for_status: bool = False, **kwargs):
        """

        Args:
            endpoint:
            payload:
            headers:
            raise_for_status:
            **kwargs:
                api_token: another input for api_token

        Returns:

        """

        assert "sync" not in payload, ".run() always runs in sync=True (to use async call .submit())"
        payload["sync"] = True
        bria_response = self.engine.post(endpoint=endpoint, payload=payload, headers=headers, **kwargs)
        if raise_for_status:
            bria_response.raise_for_status()
        return bria_response

    def submit(self, endpoint: str, payload: dict, headers: dict | None = None, raise_for_status: bool = False, **kwargs):
        assert "sync" not in payload, ".submit() always runs in sync=False (to use sync call .run())"
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
        self, response: BriaResponse, headers: dict | None = None, interval: int | float = 1, timeout: int = 60, raise_for_status: bool = True, **kwargs
    ): ...

    @overload
    def poll(self, request_id: str, headers: dict | None = None, interval: int | float = 1, timeout: int = 60, raise_for_status: bool = True, **kwargs): ...

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
        while bria_response.in_progress() or bria_response.status == Status.UNKNOWN:
            logger.debug(f"Polling request ID: {request_id}, current status: {bria_response.status}")
            time.sleep(interval)
            bria_response = call_status_service()
            if time.time() - start_time >= timeout:
                raise TimeoutError("Timeout reached while waiting for status request")

        if raise_for_status:
            bria_response.raise_for_status()
        return bria_response
