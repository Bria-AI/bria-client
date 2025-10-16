from enum import Enum

from pydantic_core import Url

from bria_sdk.engine_api.schemas.base_models import (
    APIPayloadModel,
    ContentModeratedPayloadModel,
    PromptContentModeratedPayloadModel,
)


class MaskType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"


class ObjectEraserRequestPayload(ContentModeratedPayloadModel):
    image: str
    mask: str
    mask_type: MaskType
    preserve_alpha: bool | None = None
    sync: bool | None = None


class ObjectGenFillRequestPayload(PromptContentModeratedPayloadModel):
    image: str
    mask: str
    mask_type: MaskType
    prompt: str
    negative_prompt: str | None = None
    preserve_alpha: bool | None = None
    sync: bool | None = None
    seed: int | None = None


class GetMasksRequestPayload(APIPayloadModel):
    image_url: Url
    sync: bool = True
