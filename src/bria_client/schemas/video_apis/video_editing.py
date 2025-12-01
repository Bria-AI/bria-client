from enum import Enum, IntEnum

from bria_client.schemas.base_models import APIPayloadModel


class ResolutionIncrease(IntEnum):
    TWO = 2
    FOUR = 4


class VideoOutputPreset(str, Enum):
    MP4_H264 = "mp4_h264"
    MP4_H265 = "mp4_h265"
    WEBM_VP9 = "webm_vp9"
    MOV_H265 = "mov_h265"
    MOV_PRORESKS = "mov_proresks"
    MKV_H264 = "mkv_h264"
    MKV_H265 = "mkv_h265"
    MKV_VP9 = "mkv_vp9"
    GIF = "gif"


class BackgroundColor(str, Enum):
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


class ForegroundMaskRequestPayload(APIPayloadModel):
    video: str
    output_container_and_codec: VideoOutputPreset | None = VideoOutputPreset.MP4_H264
