from contextvars import ContextVar

from bria_engine_api.apis import EngineAPIs


class BriaSDK:
    def __init__(self, api_token_ctx: ContextVar[str] | None = None, jwt_token_ctx: ContextVar[str] | None = None):
        self.engine_apis = EngineAPIs(api_token_ctx, jwt_token_ctx)
