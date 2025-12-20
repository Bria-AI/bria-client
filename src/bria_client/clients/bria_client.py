import os

from httpx_retries import Retry

from bria_client.apis.bria_backend import BriaBackend
from bria_client.engines import BriaEngine


class BriaClient(BriaBackend):
    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
        retry: Retry | None = Retry(total=3, backoff_factor=2),
    ):
        self.api_token = os.environ.get("BRIA_API_TOKEN", api_token)
        base_url = os.environ.get("BRIA_API_URL", base_url)

        engine = BriaEngine(base_url=base_url, retry=retry)
        super().__init__(engine=engine)
