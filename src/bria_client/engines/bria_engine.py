from contextvars import ContextVar

from httpx_retries import Retry

from bria_client.engines.api_engine import ApiEngine


class BriaEngine(ApiEngine):
    def __init__(self, base_url: str, api_token: str, retry: Retry | None = None):
        super().__init__(base_url=base_url, default_headers={"api_token": api_token}, retry=retry)


class BriaPlatformEngine(ApiEngine):
    def __init__(self, base_url: str, jwt_token: str, api_token: str, retry: Retry | None = None):
        super().__init__(base_url=base_url, default_headers={"jwt_token": jwt_token, "api_token": api_token}, retry=retry)


class ContextVarAuthEngine(ApiEngine):
    def __init__(self, base_url: str, api_token_ctx: ContextVar[str], retry: Retry | None = None):
        super().__init__(base_url=base_url, default_headers=lambda: {"api_token": api_token_ctx.get()}, retry=retry)


class InternalRequestEngine(ApiEngine):
    def __init__(self, base_url: str, api_token_ctx: ContextVar[str], retry: Retry | None = None):
        super().__init__(base_url=base_url, default_headers=lambda: {"api_token": api_token_ctx.get(), "X-Internal-Request": "true"}, retry=retry)
