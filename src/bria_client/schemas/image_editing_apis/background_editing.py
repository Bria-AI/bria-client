from enum import Enum

from pydantic import Field

from bria_client.schemas.image_editing_apis import ContentModeratedPayloadModel, PromptContentModeratedPayloadModel


class RemoveBackgroundRequestPayload(ContentModeratedPayloadModel):
    image: str
    preserve_alpha: bool | None = None
    sync: bool | None = None


class ReplaceBackgroundMode(str, Enum):
    BASE = "base"
    HIGH_CONTROL = "high_control"
    FAST = "fast"


class ReplaceBackgroundRequestPayload(PromptContentModeratedPayloadModel):
    image: str
    mode: ReplaceBackgroundMode | None = None
    ref_images: list[str] | None = None
    enhance_ref_images: bool | None = None
    prompt: str | None = None
    refine_prompt: bool | None = None
    negative_prompt: str | None = None
    original_quality: bool | None = None
    force_background_detection: bool | None = None
    sync: bool | None = None
    seed: int | None = None


class BlurBackgroundInput(ContentModeratedPayloadModel):
    image: str
    scale: int | None = Field(ge=1, le=5, default=None)
    preserve_alpha: bool | None = None
    sync: bool | None = None
