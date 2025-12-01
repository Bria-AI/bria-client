from bria_client.apis.video.video_generation import VideoGenerationAPI
from bria_client.apis.video.video_editing import VideoEditingAPI
from bria_client.engine_client import BriaEngineClient

__all__ = [
    "VideoGenerationAPI",
    "VideoEditingAPI",
]


class VideoAPI:
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        self.generate = VideoGenerationAPI(engine_client, status_api)
        self.edit = VideoEditingAPI(engine_client, status_api)
