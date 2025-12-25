from bria_client.payloads.bria_payload import PositivePromptInputPayload, VideoBasePayload, VideoInputPayload
from bria_client.payloads.video_editing_payload import VideoRemoveBackgroundPayload
from bria_client.toolkit.video import KeyPoint


class MaskVideoRemoveBackgroundPayload(VideoRemoveBackgroundPayload):
    pass


class VideoEraserBasePayload(VideoInputPayload, VideoBasePayload):
    auto_trim: bool | None = None


class VideoMaskByKeypointsPayload(VideoEraserBasePayload):
    key_points: list[KeyPoint]


class VideoMaskByPromptPayload(VideoEraserBasePayload, PositivePromptInputPayload):
    pass
