from bria_client.results import BriaResult


class VideoRemoveBackgroundResult(BriaResult):
    video_url: str


class VideoIncreaseResolutionResult(BriaResult):
    video_url: str


class VideoEraserResult(BriaResult):
    video_url: str
