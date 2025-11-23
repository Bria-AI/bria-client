from bria_client.apis.status_based_api import StatusBasedAPI
from bria_client.engine_client import BriaEngineClient
from bria_client.apis.status import StatusAPI
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.decorators.wait_for_status_decorator import auto_wait_for_status
from bria_client.schemas.video_apis.video_generation import (
    VideoGenerationByTailoredImageRequestPayload,
)
from bria_client.constants import BriaEngineAPIRoutes
from bria_client.exceptions.engine_api_exception import EngineAPIException
from httpx import Response


class VideoGenerationAPI(StatusBasedAPI):
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        super().__init__(engine_client, status_api)

    @auto_wait_for_status
    async def generate_by_tailored_image(
        self, payload: VideoGenerationByTailoredImageRequestPayload
    ) -> Response:
        """
        Generate a video by a tailored image

        Args:
            `payload: VideoGenerationByTailoredImageRequestPayload` - The payload for the video generation request

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response: Response = await self._engine_client.post(
            BriaEngineAPIRoutes.V2_VIDEO_GENERATE_BY_TAILOR_IMAGE,
            payload.payload_dump(),
        )
        return response
