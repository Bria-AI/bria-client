from pydantic import BaseModel, field_validator

from bria_internal.schemas.image_editing_apis import base64_pre_process, validate_url_or_base64


class BackgroundRemoveRequestPayload(BaseModel):
    image: str
    visual_input_content_moderation: bool | None = None
    visual_output_content_moderation: bool | None = None
    sync: bool = False

    @field_validator("image", mode="before")
    @classmethod
    def _validate_image(cls, v: str) -> str:
        # Not using Base64Str because it's decodes the data when using the object
        return base64_pre_process(v)

    @field_validator("image", mode="after")
    @classmethod
    def _validate_image_after(cls, v: str) -> str:
        # Not using Base64Str because it's decodes the data when using the object
        validate_url_or_base64(v)
        return v
