from bria_client.schemas.video_apis.video import KeyPoint, VideoOutputPreset
from bria_client.schemas.video_apis.video_editing import (
    BackgroundColor,
    EraseMask,
    EraseRequestPayload,
    ForegroundMaskRequestPayload,
    IncreaseResolutionRequestPayload,
    MaskByKeyPoints,
    MaskByPrompt,
    RemoveBackgroundRequestPayload,
    ResolutionIncrease,
)
from bria_client.schemas.video_apis.video_generation import (
    GenerateByTailoredImageRequestPayload,
)
from bria_client.schemas.video_apis.video_segmentation import (
    MaskByKeypointsRequestPayload,
    MaskByPromptRequestPayload,
)

__all__ = [
    "GenerateByTailoredImageRequestPayload",
    "IncreaseResolutionRequestPayload",
    "RemoveBackgroundRequestPayload",
    "ForegroundMaskRequestPayload",
    "EraseRequestPayload",
    "EraseMask",
    "MaskByPrompt",
    "MaskByKeyPoints",
    "BackgroundColor",
    "VideoOutputPreset",
    "ResolutionIncrease",
    "KeyPoint",
    "MaskByPromptRequestPayload",
    "MaskByKeypointsRequestPayload",
]
