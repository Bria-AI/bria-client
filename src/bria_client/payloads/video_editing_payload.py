from typing import Literal, TypedDict

from bria_client.payloads.bria_payload import PositivePromptInputPayload, VideoBasePayload, VideoInputPayload


class VideoIncreaseResolutionPayload(VideoInputPayload, VideoBasePayload):
    desired_increase: Literal["2", "4"] | None = None


class VideoRemoveBackgroundPayload(VideoInputPayload, VideoBasePayload):
    background_color: Literal["Transparent", "Black", "White", "Gray", "Red", "Green", "Blue", "Yellow", "Cyan", "Magenta", "Orange"] | None = None


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


class VideoEraserPayload(VideoEraserBasePayload):
    mask: str | None = None
    preserve_audio: bool | None = None


class VideoMaskByPromptPayload(VideoEraserBasePayload, PositivePromptInputPayload):
    pass
