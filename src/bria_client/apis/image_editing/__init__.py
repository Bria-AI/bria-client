from bria_client.apis.image_editing.background_editing import BackgroundEditingAPI
from bria_client.apis.image_editing.foreground_editing import ForegroundEditingAPI
from bria_client.apis.image_editing.mask_based_editing import MasksBasedEditingAPI
from bria_client.apis.image_editing.size_editing import SizeEditingAPI

__all__ = [
    "BackgroundEditingAPI",
    "ForegroundEditingAPI",
    "MasksBasedEditingAPI",
    "SizeEditingAPI",
]


class ImageEditingAPI(BackgroundEditingAPI, MasksBasedEditingAPI, ForegroundEditingAPI, SizeEditingAPI):
    pass
