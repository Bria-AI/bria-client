from bria_client.schemas.base_models import APIPayloadModel
from bria_client.schemas.video_apis.video import KeyPoint, VideoOutputPreset


class MaskByPromptRequestPayload(APIPayloadModel):
    video: str
    prompt: str
    output_container_and_codec: VideoOutputPreset | None = VideoOutputPreset.MP4_H264
    auto_trim: bool | None = False


class MaskByKeypointsRequestPayload(APIPayloadModel):
    video: str
    key_points: list[KeyPoint]
    output_container_and_codec: VideoOutputPreset | None = VideoOutputPreset.MP4_H264
    auto_trim: bool | None = False
