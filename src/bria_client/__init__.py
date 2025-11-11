from contextvars import ContextVar

from httpx_retries import Retry

from bria_client.apis.image_editing import ImageEditingAPI
from bria_client.apis.status import StatusAPI
from bria_client.clients.bria_client import BriaEngineClient


class BriaClient:
    def __init__(
        self,
        api_token_ctx: ContextVar[str] | str | None = None,
        jwt_token_ctx: ContextVar[str] | str | None = None,
        retry: Retry | None = None,
    ):
        if isinstance(api_token_ctx, str):
            api_token_ctx = ContextVar("bria_engine_api_token", default=api_token_ctx)
        if isinstance(jwt_token_ctx, str):
            jwt_token_ctx = ContextVar("bria_engine_jwt_token", default=jwt_token_ctx)

        self._client = BriaEngineClient(api_token_ctx, jwt_token_ctx, retry=retry)
        self.status = StatusAPI(self._client)
        self.image_editing = ImageEditingAPI(self._client, self.status)
