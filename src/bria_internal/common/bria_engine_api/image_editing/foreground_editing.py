from httpx import Response

from bria_internal.common.bria_engine_api.constants import BriaEngineAPIRoutes
from bria_internal.common.bria_engine_api.enable_sync_decorator import enable_run_synchronously
from bria_internal.common.bria_engine_api.engine_client import BriaEngineClient
from bria_internal.common.bria_engine_api.status.status import StatusAPI
from bria_internal.exceptions.engine_api_exception import EngineAPIException
from bria_internal.schemas.image_editing_apis.foreground_editing import CropOutRequestPayload, ReplaceForegroundRequestPayload
from bria_internal.schemas.status_api import StatusAPIResponse


class ForegroundEditingAPI:
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        self.__engine_client = engine_client
        self.__status_api = status_api

    @enable_run_synchronously
    async def replace(self, payload: ReplaceForegroundRequestPayload, wait_for_status: bool = False) -> Response | StatusAPIResponse:
        """
        Replace the foreground of an image

        Args:
            `payload: ReplaceForegroundRequestPayload` - The payload for the replace foreground request
            `wait_for_status: bool` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_REPLACE_FOREGROUND, payload.model_dump(mode="json"))

            if wait_for_status:
                response_body = response.json()
                response = await self.__status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except EngineAPIException as e:
            raise BriaEngineClient.get_custom_exception(e, payload)

    @enable_run_synchronously
    async def crop_out(self, payload: CropOutRequestPayload, wait_for_status: bool = False) -> Response | StatusAPIResponse:
        """
        Crop out the foreground of an image

        Args:
            `payload: CropOutRequestPayload` - The payload for the crop out request
            `wait_for_status: bool` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_CROP_OUT, payload.model_dump(mode="json"))

            if wait_for_status:
                response_body = response.json()
                response = await self.__status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except EngineAPIException as e:
            raise BriaEngineClient.get_custom_exception(e, payload)
