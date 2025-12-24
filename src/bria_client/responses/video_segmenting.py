from bria_client.responses import BriaResponse, BriaResult


class VideoMaskByPromptResult(BriaResult):
    mask_url: str


class VideoMaskByPromptResponse(BriaResponse[VideoMaskByPromptResult]):
    pass


class VideoMaskByKeypointsResult(BriaResult):
    mask_url: str


class VideoMaskByKeypointsResponse(BriaResponse[VideoMaskByKeypointsResult]):
    pass
