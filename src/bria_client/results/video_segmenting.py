from bria_client.results import BriaResult


class VideoMaskByPromptResult(BriaResult):
    mask_url: str


class VideoMaskByKeypointsResult(BriaResult):
    mask_url: str
