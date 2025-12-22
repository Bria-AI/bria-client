from bria_client.responses import BriaResponse, BriaResult


class BlurBackgroundResult(BriaResult):
    image_url: str


class BlurBackgroundResponse(BriaResponse[BlurBackgroundResult]):
    pass


class RemoveBackgroundResult(BriaResult):
    image_url: str


class RemoveBackgroundResponse(BriaResponse[RemoveBackgroundResult]):
    pass


class ReplaceBackgroundResult(BriaResult):
    image_url: str


class ReplaceBackgroundResponse(BriaResponse[ReplaceBackgroundResult]):
    pass
