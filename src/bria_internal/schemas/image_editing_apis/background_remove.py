from pydantic import BaseModel


class BackgroundRemoveRequestPayload(BaseModel):
    image: str
    preserve_alpha: bool | None = None
    sync: bool | None = None
    visual_input_content_moderation: bool | None = None
    visual_output_content_moderation: bool | None = None
