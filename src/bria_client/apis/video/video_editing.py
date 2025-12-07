from httpx import Response

from bria_client.apis.status import StatusAPI
from bria_client.apis.status_based_api import StatusBasedAPI
from bria_client.constants import BriaEngineAPIRoutes
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.decorators.wait_for_status_decorator import auto_wait_for_status
from bria_client.engine_client import BriaEngineClient
from bria_client.exceptions.engine_api_exception import EngineAPIException
from bria_client.schemas.video_apis.video_editing import (
    EraseRequestPayload,
    IncreaseResolutionRequestPayload,
    RemoveBackgroundRequestPayload,
)


class VideoEditingAPI(StatusBasedAPI):
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        super().__init__(engine_client, status_api)

    @enable_run_synchronously
    @auto_wait_for_status
    async def increase_resolution(self, payload: IncreaseResolutionRequestPayload) -> Response:
        """
        Increase the resolution of a video (up to 8K)

        Args:
            `payload: IncreaseResolutionRequestPayload` - The payload for the increase resolution request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_VIDEO_EDIT_INCREASE_RESOLUTION, payload.payload_dump())
            return response
        except EngineAPIException as e:
            # No content-moderation mapping for video payloads; pass-through original exception
            raise e

    @enable_run_synchronously
    @auto_wait_for_status
    async def remove_background(self, payload: RemoveBackgroundRequestPayload) -> Response:
        """
        Remove the background from a video

        Args:
            `payload: RemoveBackgroundRequestPayload` - The payload for the background removal request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_VIDEO_EDIT_REMOVE_BACKGROUND, payload.payload_dump())
            return response
        except EngineAPIException as e:
            raise e

    @enable_run_synchronously
    @auto_wait_for_status
    async def erase(self, payload: EraseRequestPayload) -> Response:
        """
        Erase designated objects or regions from a video

        Args:
            `payload: EraseRequestPayload` - The payload for the erase request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_VIDEO_EDIT_ERASE, payload.payload_dump())
            return response
        except EngineAPIException as e:
            raise e
