from pydantic import Field
from bria_client.schemas.base_models import PromptContentModeratedPayloadModel


class GenerateImageLiteRequestPayload(PromptContentModeratedPayloadModel):
    prompt: str | None = None
    images: list[str] | None = None

    structured_prompt: str | None = None  # Structured prompt as JSON string
    guidance_scale: int | None = None
    model_version: str | None = None
    aspect_ratio: str | None = None
    seed: int | None = None
    sync: bool | None = None
    ip_signal: bool | None = None
    steps_num: int | None = None


class GenerateImageRequestPayload(GenerateImageLiteRequestPayload):
    negative_prompt: str | None = None
    steps_num: int | None = None
    model_version: str | None = None


AspectRatio = Annotated[
    str,
    AfterValidator(
        lambda v: v if v in {
            "1:1", "2:3", "3:2", "3:4", "4:3",
            "4:5", "5:4", "9:16", "16:9"
        } else ValueError("Invalid aspect_ratio")
    )
]


class GenerateTailoredImageRequestPayload(PromptContentModeratedPayloadModel):
    # --- Required ---
    tailored_model_id: str

    # --- Optional ---
    model_influence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.5,
        alias="tailored_model_influence",
    )

    prompt: Optional[str] = None
    structured_prompt: Optional[str] = None
    negative_prompt: Optional[str] = None

    guidance_scale: int = Field(
        default=5,
        ge=3,
        le=5,
    )

    aspect_ratio: AspectRatio = Field(default="1:1")

    steps_num: int = Field(
        default=50,
        ge=20,
        le=50,
    )

    seed: Optional[int] = None
    sync: bool = False

    prompt_content_moderation: bool = True
    visual_output_content_moderation: bool = True

    @model_validator(mode="after")
    def validate_prompt_logic(self):
        if not self.prompt and not self.structured_prompt:
            raise ValueError(
                "One of 'prompt' or 'structured_prompt' must be provided."
            )

        if self.structured_prompt and not self.prompt and self.seed is None:
            raise ValueError(
                "When only 'structured_prompt' is provided, "
                "'seed' is required for exact recreation."
            )

        return self
