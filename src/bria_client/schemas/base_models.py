from pydantic import BaseModel


class BriaPayload(BaseModel):
    pass


class ContentModeratedPayloadModel(BriaPayload):
    visual_input_content_moderation: bool | None = None
    visual_output_content_moderation: bool | None = None

    @property
    def is_moderated(self) -> bool:
        return bool(self.visual_input_content_moderation or self.visual_output_content_moderation)


class PromptContentModeratedPayloadModel(ContentModeratedPayloadModel):
    prompt_content_moderation: bool | None = None

    @property
    def is_moderated(self) -> bool:
        return bool(super().is_moderated or self.prompt_content_moderation)
