from httpx import Response

from bria_client.apis.status_based_api import StatusBasedAPI
from bria_client.constants import BriaEngineAPIRoutes
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.decorators.wait_for_status_decorator import auto_wait_for_status
from bria_client.schemas.image.generation import GenerateImageLiteRequestPayload, GenerateImageRequestPayload, GenerateTailoredImageRequestPayload


class ImageGenerationAPI(StatusBasedAPI):
    @enable_run_synchronously
    @auto_wait_for_status
    async def generate(self, payload: GenerateImageRequestPayload) -> Response:
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
        response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_GENERATION, payload.payload_dump())
        return response

    @enable_run_synchronously
    @auto_wait_for_status
    async def generate_lite(self, payload: GenerateImageLiteRequestPayload) -> Response:
        """
        Generate an image using the lite pipeline of the Fibo Image Generation API

        Args:
            `payload: GenerateImageLiteRequestPayload` - The payload for the image generation request

        Returns:
            `Response` - Response with the image

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_GENERATION_LITE, payload.payload_dump())
        return response

    @enable_run_synchronously
    @auto_wait_for_status
    async def generate_tailored(self, payload: GenerateTailoredImageRequestPayload) -> Response:
        """
        Generate a tailored image using the Fibo Image Generation API (v2 tailored).

        Args:
            `payload: GenerateTailoredImageRequestPayload` - The payload for the tailored image generation request

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response: Response = await self._engine_client.post(
            BriaEngineAPIRoutes.V2_IMAGE_GENERATION_TAILORED,
            payload.payload_dump(),
        )
        return response
