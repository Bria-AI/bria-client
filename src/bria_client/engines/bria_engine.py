from httpx_retries import Retry

from bria_client.engines.api_engine import ApiEngine


class BriaEngine(ApiEngine):
    def __init__(self, base_url: str, api_token: str, retry: Retry | None = None):
        super().__init__(base_url=base_url, default_headers={"api_token": api_token}, retry=retry)
