from typing import Literal, TypedDict

from bria_client.payloads.bria_payload import PositivePromptInputPayload, VideoBasePayload, VideoInputPayload
from bria_client.payloads.video_editing_payload import VideoRemoveBackgroundPayload


class MaskVideoRemoveBackgroundPayload(VideoRemoveBackgroundPayload):
    background_color: Literal["mask"] | None = None


class VideoEraserBasePayload(VideoInputPayload, VideoBasePayload):
    auto_trim: bool | None = None


class KeyPoint(TypedDict):
    x: int
    y: int
    type: Literal["positive", "negative"]


class VideoMaskByKeypointsPayload(VideoEraserBasePayload):
    key_points: list[KeyPoint]


class VideoMaskByPromptPayload(VideoEraserBasePayload, PositivePromptInputPayload):
    pass
