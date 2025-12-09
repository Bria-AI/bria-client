import sys

from pydantic import BaseModel

from bria_client.schemas.base_models import APIPayloadModel
from bria_client.schemas.video_apis.video import KeyPoint, VideoOutputPreset

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum


class ResolutionIncrease(StrEnum):
    TWO = "2"
    FOUR = "4"


class BackgroundColor(StrEnum):
    TRANSPARENT = "Transparent"
    BLACK = "Black"
    WHITE = "White"
    GRAY = "Gray"
    RED = "Red"
    GREEN = "Green"
    BLUE = "Blue"
    YELLOW = "Yellow"
    CYAN = "Cyan"
    MAGENTA = "Magenta"
    ORANGE = "Orange"


class IncreaseResolutionRequestPayload(APIPayloadModel):
    video: str
    desired_increase: ResolutionIncrease | None = ResolutionIncrease.TWO
    output_container_and_codec: VideoOutputPreset | None = VideoOutputPreset.MP4_H264


class RemoveBackgroundRequestPayload(APIPayloadModel):
    video: str
    background_color: BackgroundColor | None = BackgroundColor.TRANSPARENT
    output_container_and_codec: VideoOutputPreset | None = VideoOutputPreset.WEBM_VP9


class MaskByPrompt(BaseModel):
    prompt: str


class MaskByKeyPoints(BaseModel):
    keypoints: list[KeyPoint]


class EraseMask(BaseModel):
    mask_url: str | None = None
    mask_by_prompt: MaskByPrompt | None = None
    mask_by_key_points: MaskByKeyPoints | None = None


class EraseRequestPayload(APIPayloadModel):
    video: str
    mask: EraseMask
    preserve_audio: bool | None = True
    output_container_and_codec: VideoOutputPreset | None = VideoOutputPreset.MP4_H264
    auto_trim: bool | None = False
