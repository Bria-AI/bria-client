from bria_client.schemas.base_models import PromptContentModeratedPayloadModel


class GenerateStructuredInstructionRequestPayload(PromptContentModeratedPayloadModel):
    instruction: str
    images: list[str]
    mask: str | None = None

    seed: int | None = None
    sync: bool | None = None
    ip_signal: bool | None = None

    # TODO: Change to the new base classes after the refactor is complete
    # Disabling this specific field because it doesn't have the `visual_output_content_moderation` field that exists in the parent
    visual_output_content_moderation: None = None


class GenerateStructuredPromptRequestPayload(PromptContentModeratedPayloadModel):
    prompt: str | None = None
    images: list[str] | None = None

    # The structured prompt in JSON string format
    structured_prompt: str | None = None

    seed: int | None = None
    sync: bool | None = None
    ip_signal: bool | None = None

    # TODO: Change to the new base classes after the refactor is complete
    # Disabling this specific field because it doesn't have the `visual_output_content_moderation` field that exists in the parent
    visual_output_content_moderation: None = None


class GenerateStructuredPromptFromDiffPayload(GenerateStructuredPromptRequestPayload):
    user_adjusted_structured_prompt: str | None = None
    model_version: str = ""
