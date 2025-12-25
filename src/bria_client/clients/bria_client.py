from httpx_retries import Retry

from bria_client.apis.bria_backend import BriaBackend
from bria_client.clients.settings import BriaSettings
from bria_client.engines import ApiEngine, BriaEngine


class BriaClient(BriaBackend):
    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
        retry: Retry | None = Retry(total=3, backoff_factor=2),
    ):
        self.settings = BriaSettings()
        self.api_token = self.settings.api_token or api_token
        self.base_url = self.settings.base_url or base_url
        self.retry = retry
        super().__init__()

    @property
    def _engine(self) -> ApiEngine:
        return BriaEngine(base_url=self.base_url, api_token=self.api_token, retry=self.retry)
