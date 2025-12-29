from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.image.api import ImageAPI
from bria_client.apis.v2.structured_prompt.generation import StructuredPromptGenerationAPI
from bria_client.payloads.image_generation_payload import ImageGenerationLitePayload, ImageGenerationPayload
from bria_client.results.image_generation import ImageGenerationLiteResult, ImageGenerationResult


class ImageGenerationAPI(ImageAPI, StructuredPromptGenerationAPI):
    """
    currently runs FIBO
    """

    path = "generate"

    @api_endpoint("")
    def image_generation(self, payload: ImageGenerationPayload):
        """
        Generic image generation endpoint.

        Args:
            payload (ImageGenerationPayload): The payload containing generation parameters.

        Returns:
            BriaResponse[ImageGenerationResult]: Response containing the generated image URL and metadata.
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=ImageGenerationResult)
        return response

    @api_endpoint("lite")
    def image_generation_lite(self, payload: ImageGenerationLitePayload):
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=ImageGenerationLiteResult)
        return response
