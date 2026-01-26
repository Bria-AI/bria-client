import logging
import warnings
from abc import ABC, abstractmethod

from httpx_retries import Retry

from bria_client.engines.api_engine import ApiEngine
from bria_client.engines.bria_engine import BriaEngine
from bria_client.toolkit.models import BriaResponse

logger = logging.getLogger(__name__)


class BaseBriaClient(ABC):
    """Abstract base class for Bria clients"""

    engine: ApiEngine

    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
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
        """Set up the HTTP client for this client instance"""
        pass

    @staticmethod
    def _validate_run_payload(payload: dict) -> None:
        """Validate payload for .run() method"""
        assert "sync" not in payload, ".run() always runs in sync=True (to use async call .submit())"

    @staticmethod
    def _validate_submit_payload(payload: dict) -> None:
        """Validate payload for .submit() method"""
        assert "sync" not in payload, ".submit() always runs in sync=False (to use sync call .run())"

    @staticmethod
    def _extract_request_id(target: str | BriaResponse | None, response: BriaResponse | None = None, request_id: str | None = None) -> str:
        """Extract request_id from various input formats"""
        extracted_id = request_id
        if response is not None:
            extracted_id = response.request_id
        if target is not None:
            extracted_id = target.request_id if isinstance(target, BriaResponse) else target
        if extracted_id is None:
            raise ValueError("request_id is required")
        return extracted_id
