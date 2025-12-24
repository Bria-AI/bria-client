from httpx import Response

from bria_client.apis.status import StatusAPI
from bria_client.apis.status_based_api import StatusBasedAPI
from bria_client.constants import BriaEngineAPIRoutes
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.decorators.wait_for_status_decorator import auto_wait_for_status
from bria_client.engine_client import BriaEngineClient
from bria_client.schemas.video_apis.video_segmentation import (
    MaskByKeypointsRequestPayload,
    MaskByPromptRequestPayload,
)


class VideoSegmentationAPI(StatusBasedAPI):
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        super().__init__(engine_client, status_api)

    @enable_run_synchronously
    @auto_wait_for_status(timeout=360)
    async def mask_by_prompt(self, payload: MaskByPromptRequestPayload) -> Response:
        """
        Generate a mask for a video by a prompt

        Args:
            `payload: MaskByPromptRequestPayload` - The payload for the video mask by prompt request

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_VIDEO_SEGMENT_MASK_BY_PROMPT, payload.payload_dump())
        return response

    @enable_run_synchronously
    @auto_wait_for_status(timeout=360)
    async def mask_by_keypoints(self, payload: MaskByKeypointsRequestPayload) -> Response:
        """
        Generate a mask for a video by keypoints

        Args:
            `payload: MaskByKeypointsRequestPayload` - The payload for the video mask by keypoints request

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_VIDEO_SEGMENT_MASK_BY_KEY_POINTS, payload.payload_dump())
        return response
