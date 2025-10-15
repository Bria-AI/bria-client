from bria_engine_api.apis.image_editing.background_editing import BackgroundEditingAPI
from bria_engine_api.apis.image_editing.foreground_editing import ForegroundEditingAPI
from bria_engine_api.apis.image_editing.mask_based_editing import MasksBasedEditingAPI
from bria_engine_api.apis.image_editing.size_editing import SizeEditingAPI
from bria_engine_api.apis.status import StatusAPI
from bria_engine_api.engine_client import BriaEngineClient

__all__ = [
    "BackgroundEditingAPI",
    "ForegroundEditingAPI",
    "MasksBasedEditingAPI",
    "SizeEditingAPI",
]

class ImageEditingAPI:
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        self.__engine_client = engine_client
        self.__status_api = status_api

        self.background = BackgroundEditingAPI(self.__engine_client, self.__status_api)
        self.masks = MasksBasedEditingAPI(self.__engine_client, self.__status_api)
        self.foreground = ForegroundEditingAPI(self.__engine_client, self.__status_api)
        self.size = SizeEditingAPI(self.__engine_client, self.__status_api)
 