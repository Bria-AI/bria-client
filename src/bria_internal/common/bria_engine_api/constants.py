from enum import Enum
from typing import Final

BRIA_ENGINE_PRODUCTION_URL: Final[str] = "https://engine.prod.bria-api.com/"
BRIA_ENGINE_INTEGRATION_URL: Final[str] = "https://engine.int.bria-api.com/"


class BriaEngineAPIRoutes(str, Enum):
    V1_IMAGE_EDIT_GET_MASKS = "v1/objects/mask_generator"
    V2_STATUS = "v2/status"
    V2_IMAGE_EDIT_REMOVE_BACKGROUND = "v2/image/edit/remove_background"
    V2_IMAGE_EDIT_ERASER = "v2/image/edit/erase"
    V2_IMAGE_EDIT_GEN_FILL = "v2/image/edit/gen_fill"
