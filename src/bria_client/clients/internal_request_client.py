from contextvars import ContextVar

from httpx_retries import Retry

from bria_client.apis.bria_backend import BriaBackend
from bria_client.engines.bria_engine import InternalRequestEngine


class InternalRequestClient(BriaBackend):
    def __init__(
        self,
        base_url: str,
        api_token_ctx: ContextVar[str],
        retry: Retry | None = None,
    ):
        engine = InternalRequestEngine(base_url=base_url, api_token_ctx=api_token_ctx, retry=retry)
        super().__init__(engine=engine)
