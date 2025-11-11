from contextvars import ContextVar

from httpx_retries import Retry

from bria_client.apis.bria_backend import BriaBackend
from bria_client.engines import BriaEngine


class BriaClient(BriaBackend):
    def __init__(
        self,
        base_url: str | None = None,
        api_token_ctx: ContextVar[str] | str | None = None,
        jwt_token_ctx: ContextVar[str] | str | None = None,
        retry: Retry | None = None,
    ):
        if isinstance(api_token_ctx, str):
            api_token_ctx = ContextVar("bria_engine_api_token", default=api_token_ctx)
        if isinstance(jwt_token_ctx, str):
            jwt_token_ctx = ContextVar("bria_engine_jwt_token", default=jwt_token_ctx)

        engine = BriaEngine(base_url=base_url, api_token_ctx=api_token_ctx, jwt_token_ctx=jwt_token_ctx, retry=retry)
        super().__init__(engine=engine)
