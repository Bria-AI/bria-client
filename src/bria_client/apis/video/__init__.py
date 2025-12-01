from bria_client.apis.video.video_generation import VideoGenerationAPI
from bria_client.apis.video.video_editing import VideoEditingAPI

__all__ = [
    "VideoGenerationAPI",
    "VideoEditingAPI",
]


class VideoAPI(VideoGenerationAPI, VideoEditingAPI):
    pass
