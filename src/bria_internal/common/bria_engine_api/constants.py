from enum import Enum
from typing import Final

BRIA_ENGINE_PRODUCTION_URL: Final[str] = "https://engine.prod.bria-api.com/"
BRIA_ENGINE_INTEGRATION_URL: Final[str] = "https://engine.int.bria-api.com/"


class BriaEngineAPIRoutes(str, Enum):
    V2_IMAGE_EDIT_REMOVE_BACKGROUND = "v2/image/edit/remove_background"
    V2_STATUS = "v2/status"
