import logging

from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.image.api import ImageAPI
from bria_client.payloads.image_editing_payload import (
    BlurBackgroundPayload,
    CropForegroundPayload,
    EnhanceImagePayload,
    EraseForegroundPayload,
    EraserPayload,
    ExpandImagePayload,
    GenFillPayload,
    IncreaseResPayload,
    RemoveBgPayload,
    ReplaceBgPayload,
)
from bria_client.results.image_editing import (
    BlurBackgroundResult,
    CropForegroundResult,
    EnhanceImageResult,
    EraseForegroundResult,
    EraserResult,
    ExpandImageResult,
    GenFillResult,
    IncreaseResResult,
    RemoveBackgroundResult,
    ReplaceBackgroundResult,
)


class ImageEditingAPI(ImageAPI):
    path = "edit"

    @api_endpoint("blur_background")
    def blur_background(self, payload: BlurBackgroundPayload):
        """
        Create a blur effect on the background of an image

        Args:
            payload (BlurBackgroundPayload): The payload containing:
                - image: Source image (Base64 string or URL). Formats: JPEG, JPG, PNG, WEBP
                - scale: Blur intensity from 1 to 5 (optional, default: 5)
                - preserve_alpha: Retain alpha channel if present (optional, default: True)
                - sync: Process synchronously (optional, default: False)
                - visual_input_content_moderation: Enable input moderation (optional, default: False)
                - visual_output_content_moderation: Enable output moderation (optional, default: False)

        Returns:
            BriaResponse[BlurBackgroundResult] | Awaitable[BriaResponse[BlurBackgroundResult]]:
                Response containing the blurred image URL and request_id

        Raises:
            EngineAPIException: Error returned from the API
            ContentModerationException: Content moderation failure
            TimeoutError: Request timeout exceeded
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=BlurBackgroundResult)
        return response

    @api_endpoint("remove_background")
    def remove_background(self, payload: RemoveBgPayload):
        """
        Remove the background from an image using Bria's RMBG 2.0 model

        Returns an image with the background removed and varying levels of transparency for smooth edges.
        The output can be binarized by setting a custom transparency threshold for specific use cases.

        Args:
            payload (RemoveBgPayload): The payload containing:
                - image: Source image (Base64 string or URL). Formats: JPEG, JPG, PNG, WEBP
                - preserve_alpha: Retain partial transparency from input (optional, default: True)
                - sync: Process synchronously (optional, default: False)
                - visual_input_content_moderation: Enable input moderation (optional, default: False)
                - visual_output_content_moderation: Enable output moderation (optional, default: False)

        Returns:
            BriaResponse[RemoveBackgroundResult] | Awaitable[BriaResponse[RemoveBackgroundResult]]:
                Response containing the image URL with removed background and request_id

        Raises:
            EngineAPIException: Error returned from the API
            ContentModerationException: Content moderation failure
            TimeoutError: Request timeout exceeded
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=RemoveBackgroundResult)
        return response

    @api_endpoint("replace_background")
    def replace_background(self, payload: ReplaceBgPayload):
        """
        Replace the background of an image with a generated scene or solid color

        Supports 3 generation modes: base (clean, high quality), high_control (stronger prompt adherence,
        recommended), and fast (optimal speed/quality balance). Can also replace with solid colors by
        specifying a hex code (e.g., #FF5733) in the prompt.

        Args:
            payload (ReplaceBgPayload): The payload containing:
                - image: Source image (Base64 string or URL). Formats: JPEG, JPG, PNG, WEBP
                - mode: Generation mode - "base", "high_control", "fast" (optional, default: "base")
                - prompt: Text description of new background (either prompt or ref_images required)
                - ref_images: Reference images for background (either prompt or ref_images required)
                - enhance_ref_images: Process reference images for optimal results (optional, default: True)
                - refine_prompt: Auto-adjust prompt for best results (optional, default: True)
                - prompt_content_moderation: Enable prompt moderation (optional, default: True)
                - negative_prompt: Elements to exclude from generation (optional)
                - original_quality: Retain original input size (optional, default: False)
                - sync: Process synchronously (optional, default: False)
                - visual_input_content_moderation: Enable input moderation (optional, default: False)
                - visual_output_content_moderation: Enable output moderation (optional, default: False)

        Returns:
            BriaResponse[ReplaceBackgroundResult] | Awaitable[BriaResponse[ReplaceBackgroundResult]]:
                Response containing the image URL with replaced background and request_id

        Raises:
            EngineAPIException: Error returned from the API
            ContentModerationException: Content moderation failure
            TimeoutError: Request timeout exceeded
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=ReplaceBackgroundResult)
        return response

    @api_endpoint("crop_foreground")
    def crop_foreground(self, payload: CropForegroundPayload):
        """
        Remove background and crop tightly around the foreground or region of interest

        Works with images both with and without existing backgrounds. Automatically detects the foreground
        and crops to a tight bounding box around it.

        Args:
            payload (CropForegroundPayload): The payload containing:
                - image: Source image (Base64 string or URL). Formats: JPEG, JPG, PNG, WEBP
                - padding: Padding around cropped object in pixels (optional, default: 0)
                - force_background_detection: Force background detection even if alpha channel exists (optional, default: False)
                - preserve_alpha: Retain alpha channel values from input (optional, default: True)
                - sync: Process synchronously (optional, default: False)
                - visual_input_content_moderation: Enable input moderation (optional, default: False)
                - visual_output_content_moderation: Enable output moderation (optional, default: False)

        Returns:
            BriaResponse[CropForegroundResult] | Awaitable[BriaResponse[CropForegroundResult]]:
                Response containing the cropped image URL and request_id

        Raises:
            EngineAPIException: Error returned from the API
            ContentModerationException: Content moderation failure
            TimeoutError: Request timeout exceeded
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=CropForegroundResult)
        return response

    @api_endpoint("erase_foreground")
    def erase_foreground(self, payload: EraseForegroundPayload):
        """
        Remove the primary subject (foreground) and intelligently generate the background to fill the erased area

        Returns the edited image at original resolution. Only the foreground is removed; all other areas
        remain unaltered with pixel-perfect accuracy in untouched regions.

        Args:
            payload (EraseForegroundPayload): The payload containing:
                - image: Source image (Base64 string or URL). Formats: JPEG, JPG, PNG, WEBP
                - preserve_alpha: Retain alpha channel transparency values (optional, default: True)
                - sync: Process synchronously (optional, default: False)
                - visual_input_content_moderation: Enable input moderation (optional, default: False)
                - visual_output_content_moderation: Enable output moderation (optional, default: False)

        Returns:
            BriaResponse[EraseForegroundResult] | Awaitable[BriaResponse[EraseForegroundResult]]:
                Response containing the image URL with erased foreground and request_id

        Raises:
            EngineAPIException: Error returned from the API
            ContentModerationException: Content moderation failure
            TimeoutError: Request timeout exceeded
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=EraseForegroundResult)
        return response

    @api_endpoint("expand")
    def expand_image(self, payload: ExpandImagePayload):
        """
        Expand an image using generative AI to fill new areas with contextually appropriate content

        Can expand by aspect ratio (automatically centered) or by custom canvas size with specific positioning.
        Creates unique variations instead of cropping, preserving important details.

        Args:
            payload (ExpandImagePayload): The payload containing:
                - image: Source image (Base64 string or URL). Formats: JPEG, JPG, PNG, WEBP
                - aspect_ratio: Target ratio as string ("1:1", "16:9", etc.) or float 0.5-3.0 (either this or canvas_size+position)
                - canvas_size: Output dimensions [width, height] (max 5000x5000 area, default: [1000, 1000])
                - original_image_size: Size of original within canvas [width, height] (required if no aspect_ratio)
                - original_image_location: Position [x, y] of original within canvas (required if no aspect_ratio)
                - prompt: Optional guidance text for expansion (auto-generated if empty)
                - prompt_content_moderation: Enable prompt moderation (optional, default: True)
                - seed: Control generation randomness for reproducibility (optional)
                - sync: Process synchronously (optional, default: False)
                - visual_input_content_moderation: Enable input moderation (optional, default: False)
                - visual_output_content_moderation: Enable output moderation (optional, default: False)

        Returns:
            BriaResponse[ExpandImageResult] | Awaitable[BriaResponse[ExpandImageResult]]:
                Response containing the expanded image URL and request_id

        Raises:
            EngineAPIException: Error returned from the API
            ContentModerationException: Content moderation failure
            TimeoutError: Request timeout exceeded
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=ExpandImageResult)
        return response

    @api_endpoint("enhance")
    def enhance_image(self, payload: EnhanceImagePayload):
        """
        Improve visual quality by generating richer details, sharper textures, and enhanced clarity

        Supports upscaling to higher resolutions and regenerates the image to enhance visual richness
        while preserving essential details. Unlike increase_resolution, this adds new details through
        regeneration rather than pure upscaling.

        Args:
            payload (EnhanceImagePayload): The payload containing:
                - image: Source image (Base64 string or URL). Formats: JPEG, JPG, PNG, WEBP
                - resolution: Target output resolution - "1MP", "2MP", "4MP" (optional, default: "1MP")
                - steps_num: Enhancement steps 10-50 (higher = better quality, optional, default: 20)
                - seed: Control generation randomness for reproducibility (optional)
                - preserve_alpha: Retain alpha channel transparency values (optional, default: True)
                - sync: Process synchronously (optional, default: False)
                - visual_input_content_moderation: Enable input moderation (optional, default: False)
                - visual_output_content_moderation: Enable output moderation (optional, default: False)

        Returns:
            BriaResponse[EnhanceImageResult] | Awaitable[BriaResponse[EnhanceImageResult]]:
                Response containing the enhanced image URL and request_id

        Raises:
            EngineAPIException: Error returned from the API
            ContentModerationException: Content moderation failure
            TimeoutError: Request timeout exceeded
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=EnhanceImageResult)
        return response

    @api_endpoint("increase_resolution")
    def increase_resolution(self, payload: IncreaseResPayload):
        """
        Upscale image resolution using dedicated upscaling method that preserves original content

        Unlike enhance_image, this does not add new details or regenerate content. It purely increases
        resolution while maintaining the original image content. Supports up to 8192x8192 pixels total area.

        Args:
            payload (IncreaseResPayload): The payload containing:
                - image: Source image (Base64 string or URL). Formats: JPEG, JPG, PNG, WEBP
                - desired_increase: Resolution multiplier - 2 or 4 (optional, default: 2)
                - preserve_alpha: Retain alpha channel transparency values (optional, default: True)
                - sync: Process synchronously (optional, default: False)
                - visual_input_content_moderation: Enable input moderation (optional, default: False)
                - visual_output_content_moderation: Enable output moderation (optional, default: False)

        Returns:
            BriaResponse[IncreaseResResult] | Awaitable[BriaResponse[IncreaseResResult]]:
                Response containing the upscaled image URL and request_id

        Raises:
            EngineAPIException: Error returned from the API
            ContentModerationException: Content moderation failure
            TimeoutError: Request timeout exceeded
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=IncreaseResResult)
        return response

    @api_endpoint("erase")
    def erase(self, payload: EraserPayload):
        """
        Remove specific elements or areas from an image using a mask

        The mask defines the region to be erased. The modified image is returned at original resolution,
        with all areas outside the mask remaining completely unchanged for pixel-perfect preservation.

        Args:
            payload (EraserPayload): The payload containing:
                - image: Source image (Base64 string or URL). Formats: JPEG, JPG, PNG, WEBP
                - mask: Binary mask (white=255 for erase region, black=0 for keep). Same aspect ratio as image
                - mask_type: "manual" (user-drawn) or "automatic" (algorithm-generated) (optional, default: "manual")
                - preserve_alpha: Retain alpha channel transparency values (optional, default: True)
                - sync: Process synchronously (optional, default: False)
                - visual_input_content_moderation: Enable input moderation (optional, default: False)
                - visual_output_content_moderation: Enable output moderation (optional, default: False)

        Returns:
            BriaResponse[EraserResult] | Awaitable[BriaResponse[EraserResult]]:
                Response containing the image URL with erased elements and request_id

        Raises:
            EngineAPIException: Error returned from the API
            ContentModerationException: Content moderation failure
            TimeoutError: Request timeout exceeded
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=EraserResult)
        return response

    @api_endpoint("gen_fill")
    def gen_fill(self, payload: GenFillPayload):
        """
        Generate objects by prompt in a specific region defined by a mask

        The model is optimized for blob-shaped masks. Modified image returned at original resolution with
        all areas outside the mask remaining completely unchanged for pixel-perfect preservation.

        Args:
            payload (GenFillPayload): The payload containing:
                - image: Source image (Base64 string or URL). Formats: JPEG, JPG, PNG, WEBP
                - mask: Binary mask (white=255 for generation region, black=0 for keep). Same aspect ratio as image
                - prompt: Text description for object generation (max ~50-60 words for v1, ~90-110 for v2)
                - version: Model version - 1 (clean quality) or 2 (improved quality, renders text) (optional, default: 1)
                - refine_prompt: Auto-adjust prompt for optimal results (v2 only) (optional, default: True)
                - tailored_model_id: Optional custom model ID compatible with selected version
                - prompt_content_moderation: Enable prompt moderation (optional, default: True)
                - negative_prompt: Elements to exclude from generation (optional)
                - seed: Control generation randomness for reproducibility (optional)
                - mask_type: "manual" or "automatic" (v1 only) (optional, default: "manual")
                - preserve_alpha: Retain alpha channel transparency values (optional, default: True)
                - sync: Process synchronously (optional, default: False)
                - visual_input_content_moderation: Enable input moderation (optional, default: False)
                - visual_output_content_moderation: Enable output moderation (optional, default: False)

        Returns:
            BriaResponse[GenFillResult] | Awaitable[BriaResponse[GenFillResult]]:
                Response containing the generated image URL and request_id

        Raises:
            EngineAPIException: Error returned from the API
            ContentModerationException: Content moderation failure
            TimeoutError: Request timeout exceeded
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=GenFillResult)
        return response


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger("bria_client").setLevel(logging.DEBUG)

    from bria_client import BriaClient

    client = BriaClient(base_url="https://engine.prod.bria-api.com", api_token="a10d6386dd6a11ebba800242ac130004")
    response = client.image_editing.replace_background(
        payload=ReplaceBgPayload(sync=True, image="https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png")
    )
    response.raise_for_status()
    x = 1
