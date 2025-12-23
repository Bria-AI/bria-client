from contextvars import ContextVar

from httpx_retries import Retry

from bria_client.apis.bria_backend import BriaBackend
from bria_client.engines import ApiEngine
from bria_client.engines.bria_engine import InternalRequestEngine


class InternalRequestClient(BriaBackend):
    def __init__(
        self,
        base_url: str,
        api_token_ctx: ContextVar[str],
        retry: Retry | None = None,
    ):
        self.base_url = base_url
        self.token_ctx = api_token_ctx
        self.retry = retry
        super().__init__()

    @property
    def _engine(self) -> ApiEngine:
        return InternalRequestEngine(base_url=self.base_url, api_token_ctx=self.token_ctx, retry=self.retry)
