from bria_client.results import BriaResult


class ImageGenerationResult(BriaResult):
    image_url: str
    seed: int
    structured_prompt: dict


class ImageGenerationLiteResult(ImageGenerationResult): ...
