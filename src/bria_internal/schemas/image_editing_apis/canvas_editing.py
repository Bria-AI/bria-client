from enum import Enum

from pydantic_core import Url

from bria_internal.schemas.image_editing_apis import APIPayloadModel, ContentModeratedPayloadModel, PromptContentModeratedPayloadModel


class CanvasOperationMaskType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"


class ObjectEraserRequestPayload(ContentModeratedPayloadModel):
    image: str
    mask: str
    mask_type: CanvasOperationMaskType
    preserve_alpha: bool | None = None
    sync: bool | None = None


class ObjectGenFillRequestPayload(PromptContentModeratedPayloadModel):
    image: str
    mask: str
    mask_type: CanvasOperationMaskType
    prompt: str
    negative_prompt: str | None = None
    preserve_alpha: bool | None = None
    sync: bool | None = None
    seed: int | None = None


class GetMasksRequestPayload(APIPayloadModel):
    image_url: Url
    sync: bool = True
