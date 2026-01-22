from abc import ABC

import httpx
from httpx_retries import Retry


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
