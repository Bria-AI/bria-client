from bria_client.schemas.base_models import PromptContentModeratedPayloadModel


class GenerateStructuredInstructionRequestPayload(PromptContentModeratedPayloadModel):
    instruction: str
    images: list[str]

    seed: int | None = None
    sync: bool | None = None
    ip_signal: bool | None = None

    # TODO: Should be removed
    # Disabling this specific field because it doesn't have the `visual_output_content_moderation` field in the parent
    visual_output_content_moderation: None = None
