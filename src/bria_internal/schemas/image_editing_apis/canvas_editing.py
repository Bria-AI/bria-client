from enum import Enum

from pydantic import Base64Str, BaseModel
from pydantic_core import Url


class CanvasOperationMaskType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"


class ObjectEraserRequestPayload(BaseModel):
    image: Base64Str | Url
    mask: Base64Str | Url
    mask_type: CanvasOperationMaskType
    preserve_alpha: bool | None = None
    sync: bool | None = None
    visual_input_content_moderation: bool | None = None
    visual_output_content_moderation: bool | None = None


class ObjectGenFillRequestPayload(BaseModel):
    image: Base64Str | Url
    mask: Base64Str | Url
    mask_type: CanvasOperationMaskType
    prompt: str
    prompt_content_moderation: bool | None = None
    negative_prompt: str | None = None
    preserve_alpha: bool | None = None
    sync: bool | None = None
    seed: int | None = None
    visual_input_content_moderation: bool | None = None
    visual_output_content_moderation: bool | None = None


class GetMasksRequestPayload(BaseModel):
    image_url: str
    sync: bool = True
