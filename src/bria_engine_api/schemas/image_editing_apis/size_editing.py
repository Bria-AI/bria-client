from enum import Enum

from pydantic import Field

from bria_engine_api.schemas.image_editing_apis import ContentModeratedPayloadModel, PromptContentModeratedPayloadModel


class ExpandImageRequestPayload(PromptContentModeratedPayloadModel):
    image: str
    aspect_ratio: str | float | None = None
    canvas_size: tuple[int, int] | None = None
    original_image_size: tuple[int, int] | None = None
    original_image_location: tuple[int, int] | None = None
    prompt: str | None = None
    seed: int | None = None
    negative_prompt: str | None = None
    preserve_alpha: bool | None = None
    sync: bool | None = None


class Resolution(str, Enum):
    ONE_MEGA_PIXEL = "1MP"
    TWO_MEGA_PIXEL = "2MP"
    FOUR_MEGA_PIXEL = "4MP"


class EnhanceImageRequestPayload(ContentModeratedPayloadModel):
    image: str
    sync: bool | None = None
    seed: int | None = None
    steps_num: int | None = Field(ge=10, le=50, default=None)
    resolution: Resolution | None = None
    preserve_alpha: bool | None = None


class IncreaseResolutionRequestPayload(ContentModeratedPayloadModel):
    image: str
    preserve_alpha: bool | None = None
    desired_increase: int | None = None
    sync: bool | None = None
