from bria_client.apis.status import StatusAPI
from bria_client.apis.video.video_editing import VideoEditingAPI
from bria_client.apis.video.video_generation import VideoGenerationAPI
from bria_client.apis.video.video_segmentation import VideoSegmentationAPI
from bria_client.engine_client import BriaEngineClient

__all__ = [
    "VideoGenerationAPI",
    "VideoEditingAPI",
    "VideoSegmentationAPI",
]


class VideoAPI:
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        self.generate = VideoGenerationAPI(engine_client, status_api)
        self.edit = VideoEditingAPI(engine_client, status_api)
        self.segment = VideoSegmentationAPI(engine_client, status_api)
