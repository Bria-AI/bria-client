from httpx import Response

from bria_client.apis.status import StatusAPI
from bria_client.apis.status_based_api import StatusBasedAPI
from bria_client.constants import BriaEngineAPIRoutes
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.decorators.wait_for_status_decorator import auto_wait_for_status
from bria_client.clients.engine_client import EngineClient
from bria_client.exceptions.engine_api_exception import EngineAPIException
from bria_client.schemas.image_editing_apis.foreground_editing import CropForegroundRequestPayload, EraseForegroundRequestPayload


class ForegroundEditingAPI(StatusBasedAPI):
    def __init__(self, engine_client: EngineClient, status_api: StatusAPI):
        super().__init__(engine_client, status_api)

    @enable_run_synchronously
    @auto_wait_for_status
    async def erase_foreground(self, payload: EraseForegroundRequestPayload) -> Response:
        """
        Erase the foreground of an image

        Args:
            `payload: EraseForegroundRequestPayload` - The payload for the erase foreground request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_ERASE_FOREGROUND, payload.payload_dump())
            return response
        except EngineAPIException as e:
            raise self._engine_client.get_custom_exception(e, payload)

    @enable_run_synchronously
    @auto_wait_for_status
    async def crop_foreground(self, payload: CropForegroundRequestPayload) -> Response:
        """
        Crop the foreground of an image

        Args:
            `payload: CropForegroundRequestPayload` - The payload for the crop foreground request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_CROP_FOREGROUND, payload.payload_dump())
            return response
        except EngineAPIException as e:
            raise self._engine_client.get_custom_exception(e, payload)
