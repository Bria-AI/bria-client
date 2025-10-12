from contextvars import ContextVar

from bria_internal.common.bria_engine_api.engine_client import BriaEngineClient
from bria_internal.common.bria_engine_api.image_editing import BackgroundRemoveAPI
from bria_internal.common.bria_engine_api.status.status import StatusAPI


class BriaEngineSDK:
    def __init__(self, api_token_ctx: ContextVar[str] | None = None, jwt_token_ctx: ContextVar[str] | None = None):
        self.__client = BriaEngineClient(api_token_ctx, jwt_token_ctx)
        self.status = StatusAPI(self.__client)
        self.background_remove_api = BackgroundRemoveAPI(self.__client, self.status)
