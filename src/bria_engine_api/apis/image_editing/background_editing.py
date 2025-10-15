from httpx import Response

from bria_engine_api.apis.status.status import StatusAPI
from bria_engine_api.constants import BriaEngineAPIRoutes
from bria_engine_api.enable_sync_decorator import enable_run_synchronously
from bria_engine_api.engine_client import BriaEngineClient
from bria_engine_api.exceptions.engine_api_exception import EngineAPIException
from bria_engine_api.schemas.image_editing_apis.background_editing import (
    BlurBackgroundRequestPayload,
    RemoveBackgroundRequestPayload,
    ReplaceBackgroundRequestPayload,
)
from bria_engine_api.schemas.status_api import StatusAPIResponse


class BackgroundEditingAPI:
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        self.__engine_client = engine_client
        self.__status_api = status_api

    @enable_run_synchronously
    async def remove(self, payload: RemoveBackgroundRequestPayload, wait_for_status: bool = False) -> Response | StatusAPIResponse:
        """
        Remove background from image

        Args:
            `payload: RemoveBackgroundRequestPayload` - The payload for the background remove request
            `wait_for_status: bool` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_REMOVE_BACKGROUND, payload.payload_dump())

            if wait_for_status:
                response_body = response.json()
                response = await self.__status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except EngineAPIException as e:
            raise BriaEngineClient.get_custom_exception(e, payload)

    @enable_run_synchronously
    async def replace(self, payload: ReplaceBackgroundRequestPayload, wait_for_status: bool = False) -> Response | StatusAPIResponse:
        """
        Replace the background of the image

        Args:
            `payload: ReplaceBackgroundRequestPayload` - The payload for the replace background request
            `wait_for_status: bool` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_REPLACE_BACKGROUND, payload.payload_dump())

            if wait_for_status:
                response_body = response.json()
                response = await self.__status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except EngineAPIException as e:
            raise BriaEngineClient.get_custom_exception(e, payload)

    @enable_run_synchronously
    async def blur(self, payload: BlurBackgroundRequestPayload, wait_for_status: bool = False) -> Response | StatusAPIResponse:
        """
        Blur the background of the image

        Args:
            `payload: BlurBackgroundRequestPayload` - The payload for the blur background request
            `wait_for_status: bool` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_BLUR_BACKGROUND, payload.payload_dump())

            if wait_for_status:
                response_body = response.json()
                response = await self.__status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except EngineAPIException as e:
            raise BriaEngineClient.get_custom_exception(e, payload)
