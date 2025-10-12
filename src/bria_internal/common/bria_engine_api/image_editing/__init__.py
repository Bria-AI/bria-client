from bria_internal.common.bria_engine_api.engine_client import BriaEngineClient
from bria_internal.common.bria_engine_api.image_editing.foreground_editing import ForegroundEditingAPI
from bria_internal.common.bria_engine_api.image_editing.sizing_editing import SizeEditingAPI
from bria_internal.common.bria_engine_api.status.status import StatusAPI

from .background_editing import BackgroundEditingAPI
from .canvas_editing import CanvasEditingAPI


class ImageEditingAPI:
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        self.__engine_client = engine_client
        self.__status_api = status_api

        self.background = BackgroundEditingAPI(self.__engine_client, self.__status_api)
        self.canvas = CanvasEditingAPI(self.__engine_client, self.__status_api)
        self.foreground = ForegroundEditingAPI(self.__engine_client, self.__status_api)
        self.sizing = SizeEditingAPI(self.__engine_client, self.__status_api)
