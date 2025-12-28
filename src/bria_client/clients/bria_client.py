import logging

from httpx_retries import Retry

from bria_client.apis.bria_backend import BriaBackend
from bria_client.clients.settings import BriaSettings
from bria_client.engines import ApiEngine, BriaEngine

logger = logging.getLogger(__name__)


class BriaClient(BriaBackend):
    api_token: str
    base_url: str

    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
        retry: Retry | None = Retry(total=3, backoff_factor=2),
    ):
        self.settings = BriaSettings()
        self.retry = retry
        api_token = self.settings.api_token or api_token
        base_url = self.settings.base_url or base_url
        if api_token is None:
            raise ValueError("api_token is required, please set BRIA_API_TOKEN or pass it explicitly to client")
        if base_url is None:
            raise ValueError("base_url is required, please set BRIA_BASE_URL or pass it explicitly to client")
        self.api_token = api_token
        self.base_url = base_url
        super().__init__()

    @property
    def _engine(self) -> ApiEngine:
        return BriaEngine(base_url=self.base_url, api_token=self.api_token, retry=self.retry)
