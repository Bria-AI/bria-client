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
    refined_prompt: str
    seed: int


class ReplaceBackgroundResponse(BriaResponse[ReplaceBackgroundResult]):
    pass


class CropForegroundResult(BriaResult):
    image_url: str


class CropForegroundResponse(BriaResponse[CropForegroundResult]):
    pass


class EraseForegroundResult(BriaResult):
    image_url: str


class EraseForegroundResponse(BriaResponse[EraseForegroundResult]):
    pass


class ExpandImageResult(BriaResult):
    image_url: str


class ExpandImageResponse(BriaResponse[ExpandImageResult]):
    pass


class EnhanceImageResult(BriaResult):
    image_url: str


class EnhanceImageResponse(BriaResponse[EnhanceImageResult]):
    pass


class IncreaseResResult(BriaResult):
    image_url: str


class IncreaseResResponse(BriaResponse[IncreaseResResult]):
    pass


class EraserResult(BriaResult):
    image_url: str


class EraserResponse(BriaResponse[EraserResult]):
    pass


class GenFillResult(BriaResult):
    image_url: str


class GenFillResponse(BriaResponse[GenFillResult]):
    pass
