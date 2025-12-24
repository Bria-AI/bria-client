from bria_client.responses import BriaResponse, BriaResult


class VideoRemoveBackgroundResult(BriaResult):
    video_url: str


class VideoRemoveBackgroundResponse(BriaResponse[VideoRemoveBackgroundResult]):
    pass


class VideoIncreaseResolutionResult(BriaResult):
    video_url: str


class VideoIncreaseResolutionResponse(BriaResponse[VideoIncreaseResolutionResult]):
    pass


class VideoEraserResult(BriaResult):
    video_url: str


class VideoEraserResponse(BriaResponse[VideoEraserResult]):
    pass
