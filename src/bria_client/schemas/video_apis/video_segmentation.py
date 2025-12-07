from pydantic import BaseModel

from bria_client.schemas.base_models import APIPayloadModel
from bria_client.schemas.video_apis.video_editing import VideoOutputPreset


class KeyPoint(BaseModel):
    x: int
    y: int
    width: int
    height: int


class MaskByPromptRequestPayload(APIPayloadModel):
    video: str
    prompt: str
    output_container_and_codec: VideoOutputPreset | None = VideoOutputPreset.MP4_H264


class MaskByKeypointsRequestPayload(APIPayloadModel):
    video: str
    keypoints: list[KeyPoint]
    output_container_and_codec: VideoOutputPreset | None = VideoOutputPreset.MP4_H264
