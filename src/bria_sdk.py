from contextvars import ContextVar

from .bria_engine_api.apis.image_editing import ImageEditingAPI
from .bria_engine_api.apis.status.status import StatusAPI
from .bria_engine_api.engine_client import BriaEngineClient


class BriaSDK:
    def __init__(self, api_token_ctx: ContextVar[str] | None = None, jwt_token_ctx: ContextVar[str] | None = None):
        self.__client = BriaEngineClient(api_token_ctx, jwt_token_ctx)
        self.status = StatusAPI(self.__client)
        self.image_editing = ImageEditingAPI(self.__client, self.status)
