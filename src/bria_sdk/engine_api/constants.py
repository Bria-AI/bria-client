from enum import Enum
from typing import Final

BRIA_ENGINE_PRODUCTION_URL: Final[str] = "https://engine.prod.bria-api.com/"


class BriaEngineAPIRoutes(str, Enum):
    V1_IMAGE_EDIT_GET_MASKS = "v1/objects/mask_generator"
    V2_STATUS = "v2/status"
    V2_IMAGE_EDIT_REMOVE_BACKGROUND = "v2/image/edit/remove_background"
    V2_IMAGE_EDIT_ERASER = "v2/image/edit/erase"
    V2_IMAGE_EDIT_GEN_FILL = "v2/image/edit/gen_fill"
    V2_IMAGE_EDIT_REPLACE_BACKGROUND = "v2/image/edit/replace_background"
    V2_IMAGE_EDIT_REPLACE_FOREGROUND = "v2/image/edit/erase_foreground"
    V2_IMAGE_EDIT_BLUR_BACKGROUND = "v2/image/edit/blur_background"
    V2_IMAGE_EDIT_EXPAND_IMAGE = "v2/image/edit/expand"
    V2_IMAGE_EDIT_ENHANCE_IMAGE = "v2/image/edit/enhance"
    V2_IMAGE_EDIT_INCREASE_RESOLUTION = "v2/image/edit/increase_resolution"
    V2_IMAGE_EDIT_CROP_OUT = "v2/image/edit/crop_foreground"
