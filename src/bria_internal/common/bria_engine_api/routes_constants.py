from enum import Enum


class BriaEngineAPIRoutes(str, Enum):
    V2_IMAGE_EDIT_REMOVE_BACKGROUND = "v2/image/edit/remove_background"
    V2_STATUS = "v2/status"
