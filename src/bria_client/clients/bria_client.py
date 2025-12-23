import os

from httpx_retries import Retry

from bria_client.apis.bria_backend import BriaBackend
from bria_client.engines import ApiEngine, BriaEngine


class BriaClient(BriaBackend):
    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
        retry: Retry | None = Retry(total=3, backoff_factor=2),
    ):
        self.api_token = os.environ.get("BRIA_API_TOKEN", api_token)
        self.base_url = os.environ.get("BRIA_API_URL", base_url)
        self.retry = retry
        super().__init__()

    @property
    def _engine(self) -> ApiEngine:
        return BriaEngine(base_url=self.base_url, api_token=self.api_token, retry=self.retry)
