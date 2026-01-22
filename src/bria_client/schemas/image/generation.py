from bria_client.schemas.base_models import PromptContentModeratedPayloadModel


class GenerateImageLiteRequestPayload(PromptContentModeratedPayloadModel):
    prompt: str | None = None
    images: list[str] | None = None

    structured_prompt: str | None = None  # Structured prompt as JSON string
    guidance_scale: int | None = None
    model_version: str | None = None
    aspect_ratio: str | None = None
    seed: int | None = None
    sync: bool | None = None
    ip_signal: bool | None = None
    steps_num: int | None = None


class GenerateImageRequestPayload(GenerateImageLiteRequestPayload):
    negative_prompt: str | None = None
    steps_num: int | None = None
    model_version: str | None = None