from bria_client.responses import BriaResponse, BriaResult


class BlurBackgroundResult(BriaResult):
    image_url: str


class BlurBackgroundResponse(BriaResponse[BlurBackgroundResult]):
    pass
