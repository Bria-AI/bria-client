from typing import Literal

from pydantic import BaseModel

from bria_client.payloads.bria_payload import (
    ImageBasePayload,
    ImageDrivenPayload,
    ImageInputPayload,
    MaskInputPayload,
    PreserveInputImageAlphaParam,
    PromptInputPayload,
    RemoveBackgroundDetectionParam,
    SeedInputParam,
)


class BlurBackgroundPayload(ImageBasePayload, ImageInputPayload, PreserveInputImageAlphaParam):
    scale: int | None = None


class RemoveBgPayload(ImageBasePayload, ImageInputPayload, PreserveInputImageAlphaParam):
    pass


class ReplaceBgPayload(ImageInputPayload, PromptInputPayload, ImageBasePayload, ImageDrivenPayload, RemoveBackgroundDetectionParam):
    fast: bool | None = None
    refine_prompt: bool | None = None
    mode: Literal["base", "fast", "high_control"] | None = None


class ExpandImagePayload(ImageInputPayload, ImageBasePayload, PreserveInputImageAlphaParam, PromptInputPayload):
    aspect_ratio: float | str | None = None
    canvas_size: tuple[int, int] | None = None
    original_image_size: tuple[int, int] | None = None
    original_image_location: tuple[int, int] | None = None
    retain_original_area_quality: bool | None = None
    upscale_result: bool | None = None


class IncreaseResPayload(ImageInputPayload, ImageBasePayload, PreserveInputImageAlphaParam):
    desired_increase: Literal[2, 4] | None = None


class EnhanceImagePayload(ImageInputPayload, ImageBasePayload, PreserveInputImageAlphaParam, SeedInputParam):
    resolution: str | None = None


class EraserPayload(ImageInputPayload, ImageBasePayload, MaskInputPayload, PreserveInputImageAlphaParam):
    pass


class GenFillPayload(ImageBasePayload, ImageInputPayload, PromptInputPayload, MaskInputPayload, PreserveInputImageAlphaParam):
    version: Literal[1, 2] | None = None
    tailored_model_id: str | None = None
    tailored_model_influence: float | None = None
    refine_prompt: bool | None = None
    pixel_preservation: bool | None = None
    tailored_model_prefix: str | None = None


class CropForegroundPayload(ImageBasePayload, ImageInputPayload, PreserveInputImageAlphaParam, RemoveBackgroundDetectionParam):
    padding: list[int] | int | None = None


class EraseForegroundPayload(ImageInputPayload, ImageBasePayload, PreserveInputImageAlphaParam, RemoveBackgroundDetectionParam):
    pass


class MaskGenPayload(BaseModel):
    sync: bool | None = None
    file: str | None = None
    image_url: str | None = None
    content_moderation: bool | None = None
