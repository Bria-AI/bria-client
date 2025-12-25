from bria_client.results import BriaResult


class BlurBackgroundResult(BriaResult):
    image_url: str


class RemoveBackgroundResult(BriaResult):
    image_url: str


class ReplaceBackgroundResult(BriaResult):
    image_url: str
    refined_prompt: str
    seed: int


class CropForegroundResult(BriaResult):
    image_url: str


class EraseForegroundResult(BriaResult):
    image_url: str


class ExpandImageResult(BriaResult):
    image_url: str


class EnhanceImageResult(BriaResult):
    image_url: str


class IncreaseResResult(BriaResult):
    image_url: str


class EraserResult(BriaResult):
    image_url: str


class GenFillResult(BriaResult):
    image_url: str
