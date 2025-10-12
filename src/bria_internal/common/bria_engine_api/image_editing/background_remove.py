from httpx import HTTPStatusError, Response

from bria_internal.common.bria_engine_api.constants import BriaEngineAPIRoutes
from bria_internal.common.bria_engine_api.enable_sync_decorator import enable_run_synchronously
from bria_internal.common.bria_engine_api.engine_client import BriaEngineClient
from bria_internal.common.bria_engine_api.status.status import StatusAPI
from bria_internal.schemas.image_editing_apis.background_remove import BackgroundRemoveRequestPayload
from bria_internal.schemas.status_api import StatusAPIResponse


class BackgroundRemoveAPI:
    def __init__(self, engine_api: BriaEngineClient, status_api: StatusAPI):
        self.engine_api = engine_api
        self.status_api = status_api

    @enable_run_synchronously
    async def remove_background_by_image_url_v2(self, payload: BackgroundRemoveRequestPayload, wait_for_status: bool = False) -> Response | StatusAPIResponse:
        """
        Remove the background from the image

        Args:
            payload: BackgroundRemoveRequestPayload - The payload for the background remove request
            wait_for_status: bool - Whether to wait for the status request (locally)

        Returns:
            StatusAPIResponse if the wait_for_status is True, else returns the httpx.Response from the API,

        Raises:
            EngineAPIBaseException: In cases error is returned from the API
            TimeoutError: If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.engine_api.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_REMOVE_BACKGROUND, payload.model_dump())

            if wait_for_status:
                response_body = response.json()
                response = await self.status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except HTTPStatusError as e:
            if e.response.status_code == 422:
                # TODO: Add content moderation specific check here
                pass

            raise e
