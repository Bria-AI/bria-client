from httpx import Response

from bria_client.apis.status_based_api import StatusBasedAPI
from bria_client.constants import BriaEngineAPIRoutes
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.decorators.wait_for_status_decorator import auto_wait_for_status
from bria_client.schemas.image.generation import GenerateImageRequestPayload


class ImageGenerationAPI(StatusBasedAPI):
    @enable_run_synchronously
    @auto_wait_for_status
    async def generate(self, payload: GenerateImageRequestPayload, lite: bool = False) -> Response:
        """
        Generate an image using the Fibo Image Generation API

        Args:
            `payload: GenerateImageRequestPayload` - The payload for the image generation request
            `lite: bool` - Whether to use the lite version of the API

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        if lite:
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_GENERATION_LITE, payload.payload_dump())
            return response

        response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_GENERATION, payload.payload_dump())
        return response
