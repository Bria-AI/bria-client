import sys

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum

from bria_client.schemas.base_models import PromptContentModeratedPayloadModel


class ModelVersion(StrEnum):
    FIBO_EDIT = "FIBO-edit"


class EditRequestPayload(PromptContentModeratedPayloadModel):
    images: list[str]
    instruction: str | None = None
    structured_instruction: str | None = None
    mask: str | None = None
    aspect_ratio: str | None = None
    negative_prompt: str | None = None
    guidance_scale: int | None = None
    model_version: ModelVersion | None = None
    steps_num: int | None
    seed: int | None = None
    sync: bool | None = None
    ip_signal: bool | None = None
