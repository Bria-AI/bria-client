from abc import abstractmethod
from contextvars import ContextVar

from httpx_retries import Retry

from bria_client.engines.base.async_http_request import AsyncHTTPRequest
from bria_client.exceptions.engine_api_exception import EngineAPIException
from bria_client.schemas.image_editing_apis import ContentModeratedPayloadModel
from bria_client.settings import BriaEngineSettings


class ApiEngine(AsyncHTTPRequest):
    def __init__(
        self,
        base_url: str | None = None,
        api_token_ctx: ContextVar[str] | None = None,
        jwt_token_ctx: ContextVar[str] | None = None,
        retry: Retry | None = None,
    ) -> None:
        self.settings = BriaEngineSettings()

        if api_token_ctx is None and self.settings.API_KEY:
            api_token_ctx = ContextVar("bria_engine_api_token", default=self.settings.API_KEY)
        elif api_token_ctx is None and jwt_token_ctx is None:
            raise ValueError("Bria Engine API key in not provided and JWT token is not provided")

        if base_url is None:
            base_url = str(self.settings.URL)

        self.api_token_ctx = api_token_ctx
        self.jwt_token_ctx = jwt_token_ctx
        self.retry = retry

        super().__init__(base_url=base_url, retry=retry)

    @property
    def headers(self) -> dict:
        if self.api_token is None and self.jwt_token is None:
            raise ValueError("Authentication token is not set")

        headers = {"api_token": self.api_token} if self.api_token else {"jwt": self.jwt_token}
        return headers

    @property
    def api_token(self) -> str:
        try:
            if self.api_token_ctx is None:
                return None

            return self.api_token_ctx.get()
        except LookupError:
            return None

    @property
    def jwt_token(self) -> str | None:
        try:
            if self.jwt_token_ctx is None:
                return None

            return self.jwt_token_ctx.get()
        except LookupError:
            # ContextVar exists but not initialized yet
            return None

    @abstractmethod
    def get_custom_exception(self, e: EngineAPIException, payload: ContentModeratedPayloadModel) -> EngineAPIException:
        pass
