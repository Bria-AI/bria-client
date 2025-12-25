from pydantic import ConfigDict

from bria_client.payloads.bria_payload import PositivePromptInputPayload, VideoBasePayload, VideoInputPayload
from bria_client.toolkit.specifics import IncreaseResDesiredIncrease
from bria_client.toolkit.video import KeyPoint, VideoBackgroundColor


class VideoIncreaseResolutionPayload(VideoInputPayload, VideoBasePayload):
    desired_increase: IncreaseResDesiredIncrease | None = None


class VideoRemoveBackgroundPayload(VideoInputPayload, VideoBasePayload):
    background_color: VideoBackgroundColor | None = None


class VideoEraserBasePayload(VideoInputPayload, VideoBasePayload):
    auto_trim: bool | None = None


class VideoEraserPayload(VideoEraserBasePayload):
    mask: str | None = None
    preserve_audio: bool | None = None


class VideoMaskByKeypointsPayload(VideoEraserBasePayload):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    key_points: list[KeyPoint]


class VideoMaskByPromptPayload(VideoEraserBasePayload, PositivePromptInputPayload):
    pass
