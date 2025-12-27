from pydantic import ConfigDict

from bria_client.toolkit.image import ImageMaskKind, ImageOutputType, ImageSource
from bria_client.toolkit.models import ExcludeNoneBaseModel
from bria_client.toolkit.video import VideoOutputContainerAndCodec


class BriaPayload(ExcludeNoneBaseModel):
    model_config = ConfigDict(use_enum_values=True, arbitrary_types_allowed=True)


class BriaV2BasePayload(BriaPayload):
    sync: bool | None = None


class ImageBasePayload(BriaV2BasePayload):
    output_type: ImageOutputType | None = None
    visual_output_content_moderation: bool | None = None
    visual_output_content_moderation_threshold: float | None = None


class ImageInputPayload(BriaV2BasePayload):
    image: ImageSource | None = None
    visual_input_content_moderation_threshold: float | None = None
    visual_input_content_moderation: bool | None = None
    preserve_color_bit_depth: bool | None = None


class MaskInputPayload(BriaV2BasePayload):
    mask: ImageSource | None = None
    mask_type: ImageMaskKind | None = None


class PreserveInputImageAlphaParam(BriaPayload):
    preserve_alpha: bool | None = None


class RemoveBackgroundDetectionParam(BriaPayload):
    force_background_detection: bool | None = None


class SeedInputParam(BriaPayload):
    seed: int | None = None


class PositivePromptInputPayload(BriaPayload):
    prompt: str | None = None
    prompt_content_moderation: bool | None = None


class PromptInputPayload(PositivePromptInputPayload):
    negative_prompt: str | None = None
    steps_num: int | None = None


class IpSignalInputPayload(PromptInputPayload):
    ip_signal: bool | None = None


class ImageDrivenPayload(BriaPayload):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    ref_images: list[ImageSource] | None = None
    enhance_ref_images: bool | None = None
    ref_image_influence: float | None = None


class VideoBasePayload(BriaV2BasePayload):
    output_container_and_codec: VideoOutputContainerAndCodec | None = None


class VideoInputPayload(BriaV2BasePayload):
    video: str | None = None


if __name__ == "__main__":
    import io

    import requests
    from PIL import Image

    def download_image_url(url: str) -> Image.Image:
        res = requests.get(url, timeout=10.0)
        if res.status_code != requests.codes.ok:
            raise Exception("failed to download image")
        return Image.open(io.BytesIO(res.content))

    image = download_image_url("https://bria-image-repository.s3.amazonaws.com/images/8f893e628137ead8.png")
    x = ImageInputPayload(image=image)
    x.model_dump()
    a = 1
