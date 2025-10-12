from typing import Awaitable

from httpx import HTTPStatusError, Response

from bria_internal.common.bria_engine_api.constants import BriaEngineAPIRoutes
from bria_internal.common.bria_engine_api.enable_sync_decorator import enable_run_synchronously
from bria_internal.common.bria_engine_api.engine_client import BriaEngineClient
from bria_internal.common.bria_engine_api.status.status import StatusAPI
from bria_internal.schemas.image_editing_apis.size_editing import EnhanceImageRequestPayload, ExpandImageRequestPayload, IncreaseResolutionRequestPayload
from bria_internal.schemas.status_api import StatusAPIResponse


class SizeEditingAPI:
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        self.__engine_client = engine_client
        self.__status_api = status_api

    @enable_run_synchronously
    async def expand_image(self, payload: ExpandImageRequestPayload, wait_for_status: bool = False) -> Awaitable[Response | StatusAPIResponse]:
        """
        Expand the provided image to a new size by aspect ratio or by pixel sizes

        Args:
            `payload: ExpandImageRequestPayload` - The payload for the expand image request
            `wait_for_status: bool` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - StatusAPIResponse if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_EXPAND_IMAGE, payload.payload_dump())

            if wait_for_status:
                response_body = response.json()
                response = await self.__status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except HTTPStatusError as e:
            raise BriaEngineClient.handle_custom_exceptions(e, payload)

    @enable_run_synchronously
    async def enhance_image(self, payload: EnhanceImageRequestPayload, wait_for_status: bool = False) -> Awaitable[Response | StatusAPIResponse]:
        """
        Enhance the provided image by improving the quality and resolution

        Args:
            `payload: EnhanceImageRequestPayload` - The payload for the enhance image request
            `wait_for_status: bool` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - StatusAPIResponse if wait_for_status is True, else httpx.Response

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_ENHANCE_IMAGE, payload.payload_dump())

            if wait_for_status:
                response_body = response.json()
                response = await self.__status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except HTTPStatusError as e:
            raise BriaEngineClient.handle_custom_exceptions(e, payload)

    @enable_run_synchronously
    async def increase_resolution(self, payload: IncreaseResolutionRequestPayload, wait_for_status: bool = False) -> Awaitable[Response | StatusAPIResponse]:
        """
        Increase the resolution of the provided image

        Args:
            `payload: IncreaseResolutionRequestPayload` - The payload for the increase resolution request
            `wait_for_status: bool` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API
            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable
            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_INCREASE_RESOLUTION, payload.payload_dump())

            if wait_for_status:
                response_body = response.json()
                response = await self.__status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except HTTPStatusError as e:
            raise BriaEngineClient.handle_custom_exceptions(e, payload)
