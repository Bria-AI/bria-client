from bria_engine_api.apis.image_editing.background_editing import BackgroundEditingAPI
from bria_engine_api.apis.image_editing.foreground_editing import ForegroundEditingAPI
from bria_engine_api.apis.image_editing.mask_based_editing import MasksBasedEditingAPI
from bria_engine_api.apis.image_editing.size_editing import SizeEditingAPI
from bria_engine_api.apis.status import StatusAPI
from bria_engine_api.apis.status_based_api import StatusBasedAPI
from bria_engine_api.engine_client import BriaEngineClient

__all__ = [
    "BackgroundEditingAPI",
    "ForegroundEditingAPI",
    "MasksBasedEditingAPI",
    "SizeEditingAPI",
]

class ImageEditingAPI(StatusBasedAPI):
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        super().__init__(engine_client, status_api)

        self.background = BackgroundEditingAPI(self._engine_client, self._status_api)
        self.masks = MasksBasedEditingAPI(self._engine_client, self._status_api)
        self.foreground = ForegroundEditingAPI(self._engine_client, self._status_api)
        self.size = SizeEditingAPI(self._engine_client, self._status_api)
 