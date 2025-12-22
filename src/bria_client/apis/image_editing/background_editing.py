from httpx import Response

from bria_client.apis.status.status_based_api import StatusBasedAPI
from bria_client.constants import BriaEngineAPIRoutes
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.decorators.wait_for_status_decorator import auto_wait_for_status
from bria_client.engines.base import ApiEngine
from bria_client.exceptions.old.engine_api_exception import EngineAPIException
from bria_client.schemas.image_editing_apis.background_editing import (
    BlurBackgroundInput,
    ReplaceBackgroundRequestPayload,
)


class BackgroundEditingAPI(StatusBasedAPI):
    def __init__(self, engine_client: ApiEngine, status_api: "StatusAPI"):
        super().__init__(engine_client, status_api)

    @enable_run_synchronously
    @auto_wait_for_status
    async def replace_background(self, payload: ReplaceBackgroundRequestPayload) -> Response:
        """
        Replace the background of the image

        Args:
            `payload: ReplaceBackgroundRequestPayload` - The payload for the replace background request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_REPLACE_BACKGROUND, payload.payload_dump())
            return response
        except EngineAPIException as e:
            raise self._engine_client.custom_exception_handle(e, payload)

    @enable_run_synchronously
    @auto_wait_for_status
    async def blur_background(self, payload: BlurBackgroundInput) -> Response:
        """
        Blur the background of the image

        Args:
            `payload: BlurBackgroundRequestPayload` - The payload for the blur background request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_BLUR_BACKGROUND, payload.payload_dump())
            return response
        except EngineAPIException as e:
            raise self._engine_client.custom_exception_handle(e, payload)
