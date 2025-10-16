from httpx import Response

from bria_sdk.engine_api.apis.status import StatusAPI
from bria_sdk.engine_api.apis.status_based_api import StatusBasedAPI
from bria_sdk.engine_api.constants import BriaEngineAPIRoutes
from bria_sdk.engine_api.decorators.enable_sync_decorator import enable_run_synchronously
from bria_sdk.engine_api.decorators.wait_for_status_decorator import auto_wait_for_status
from bria_sdk.engine_api.engine_client import BriaEngineClient
from bria_sdk.engine_api.exceptions.engine_api_exception import EngineAPIException
from bria_sdk.engine_api.schemas.image_editing_apis.foreground_editing import CropOutRequestPayload, ReplaceForegroundRequestPayload


class ForegroundEditingAPI(StatusBasedAPI):
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        super().__init__(engine_client, status_api)

    @enable_run_synchronously
    @auto_wait_for_status
    async def replace(self, payload: ReplaceForegroundRequestPayload) -> Response:
        """
        Replace the foreground of an image

        Args:
            `payload: ReplaceForegroundRequestPayload` - The payload for the replace foreground request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_REPLACE_FOREGROUND, payload.payload_dump())
            return response
        except EngineAPIException as e:
            raise BriaEngineClient.get_custom_exception(e, payload)

    @enable_run_synchronously
    @auto_wait_for_status
    async def crop_out(self, payload: CropOutRequestPayload) -> Response:
        """
        Crop out the foreground of an image

        Args:
            `payload: CropOutRequestPayload` - The payload for the crop out request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_CROP_OUT, payload.payload_dump())
            return response
        except EngineAPIException as e:
            raise BriaEngineClient.get_custom_exception(e, payload)
