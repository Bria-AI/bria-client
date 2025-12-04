from enum import Enum

from pydantic import BaseModel


class KeyPoint(BaseModel):
    x: int
    y: int
    width: int
    height: int


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
