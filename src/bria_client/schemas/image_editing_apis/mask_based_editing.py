from enum import Enum
from typing import Literal

from pydantic_core import Url

from bria_client.schemas.base_models import (
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
    prompt: str
    version: Literal[1, 2] = 2
    refine_prompt: bool = True
    tailored_model_id: str | None = None
    negative_prompt: str | None = None
    preserve_alpha: bool | None = None
    sync: bool | None = None
    seed: int | None = None
    mask_type: MaskType | None = None


class GetMasksRequestPayload(APIPayloadModel):
    image_url: Url
    sync: bool = True
