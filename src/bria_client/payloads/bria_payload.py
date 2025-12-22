from typing import Literal

from pydantic import BaseModel, ConfigDict

from bria_client.toolkit.image_source import ImageSource


class BriaPayload(BaseModel):
    pass


class BriaV2BasePayload(BriaPayload):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    sync: bool | None = None


class ImageBasePayload(BriaV2BasePayload):
    output_type: Literal["png", "jpeg"] | None = None
    visual_output_content_moderation: bool | None = None
    visual_output_content_moderation_threshold: float | None = None


class ImageInputPayload(BriaV2BasePayload):
    image: ImageSource | None = None
    visual_input_content_moderation_threshold: float | None = None
    visual_input_content_moderation: bool | None = None
    preserve_color_bit_depth: bool | None = None


class MaskInputPayload(BriaV2BasePayload):
    mask: ImageSource | None = None
    mask_type: Literal["manual", "automatic", "automatic_full"] | None = None


class PreserveInputImageAlphaParam(BaseModel):
    preserve_alpha: bool | None = None


class RemoveBackgroundDetectionParam(BaseModel):
    force_background_detection: bool | None = None


class SeedInputParam(BaseModel):
    seed: int | None = None


class PositivePromptInputPayload(BaseModel):
    prompt: str | None = None
    prompt_content_moderation: bool | None = None


class PromptInputPayload(PositivePromptInputPayload):
    negative_prompt: str | None = None
    steps_num: int | None = None


class IpSignalInputPayload(PromptInputPayload):
    ip_signal: bool | None = None


class ImageDrivenPayload(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    ref_images: list[ImageSource] | None = None
    enhance_ref_images: bool | None = None
    ref_image_influence: float | None = None
