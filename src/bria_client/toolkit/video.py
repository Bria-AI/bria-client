import sys
from typing import Literal

from typing_extensions import TypedDict

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum


class KeyPoint(TypedDict):
    x: int
    y: int
    type: Literal["positive", "negative"]


class VideoOutputContainerAndCodec(StrEnum):
    MP4_H265 = "mp4_h265"
    MP4_H264 = "mp4_h264"
    WEBM_VP9 = "webm_vp9"
    MOV_H265 = "mov_h265"
    MOV_PRORESKS = "mov_proresks"
    MKV_H265 = "mkv_h265"
    MKV_H264 = "mkv_h264"
    MKV_VP9 = "mkv_vp9"
    GIF = "gif"
    AVI_H264 = "avi_h264"


class VideoBackgroundColor(StrEnum):
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
