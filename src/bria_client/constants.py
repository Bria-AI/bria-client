import sys
from typing import Final

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum

BRIA_ENGINE_PRODUCTION_URL: Final[str] = "https://engine.prod.bria-api.com/"


class BriaEngineAPIRoutes(StrEnum):
    # V1 Routes
    V1_IMAGE_EDIT_GET_MASKS = "v1/objects/mask_generator"

    # V2 Status
    V2_STATUS = "v2/status"

    # V2 Image Edit Routes
    V2_IMAGE_EDIT_REMOVE_BACKGROUND = "v2/image/edit/remove_background"
    V2_IMAGE_EDIT_ERASER = "v2/image/edit/erase"
    V2_IMAGE_EDIT_GEN_FILL = "v2/image/edit/gen_fill"
    V2_IMAGE_EDIT_REPLACE_BACKGROUND = "v2/image/edit/replace_background"
    V2_IMAGE_EDIT_ERASE_FOREGROUND = "v2/image/edit/erase_foreground"
    V2_IMAGE_EDIT_BLUR_BACKGROUND = "v2/image/edit/blur_background"
    V2_IMAGE_EDIT_EXPAND_IMAGE = "v2/image/edit/expand"
    V2_IMAGE_EDIT_ENHANCE_IMAGE = "v2/image/edit/enhance"
    V2_IMAGE_EDIT_INCREASE_RESOLUTION = "v2/image/edit/increase_resolution"
    V2_IMAGE_EDIT_CROP_FOREGROUND = "v2/image/edit/crop_foreground"

    # V2 Video Generation Routes
    V2_VIDEO_GENERATE_BY_TAILOR_IMAGE = "v2/video/generate/tailored/image-to-video"
    V2_VIDEO_GENERATE_FOREGROUND_MASK = "v2/video/generate/foreground_mask"

    # V2 Video Edit Routes
    V2_VIDEO_EDIT_INCREASE_RESOLUTION = "v2/video/edit/increase_resolution"
    V2_VIDEO_EDIT_REMOVE_BACKGROUND = "v2/video/edit/remove_background"

    # V2 Video Segmentation Routes
    V2_VIDEO_SEGMENT_MASK_BY_PROMPT = "v2/video/segment/mask_by_prompt"
    V2_VIDEO_SEGMENT_MASK_BY_KEYPOINTS = "v2/video/segment/mask_by_keypoints"
