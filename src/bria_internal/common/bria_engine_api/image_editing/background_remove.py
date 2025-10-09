from typing import TYPE_CHECKING

from httpx import HTTPStatusError, Response

from bria_internal.common.bria_engine_api.enable_sync_decorator import enable_run_synchronously
from bria_internal.common.bria_engine_api.routes_constants import BriaEngineAPIRoutes
from bria_internal.exceptions.engine_api_exception import EngineAPIBaseException
from bria_internal.schemas.image_editing_apis.background_remove import BackgroundRemoveRequestPayload
from bria_internal.schemas.status_api import StatusAPIResponse

if TYPE_CHECKING:
    from bria_internal.common.bria_engine_api import BriaEngineClient


class BackgroundRemoveAPI:
    def __init__(self, engine_api: "BriaEngineClient"):
        self.engine_api = engine_api

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
            ContentModerationError: If the content moderation fails (status code 422)
            TimeoutError: If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.engine_api.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_REMOVE_BACKGROUND, payload.model_dump())
            response_body = response.json()

            if wait_for_status:
                response = await self.engine_api.status.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except HTTPStatusError as e:
            if e.response.status_code == 422:
                # TODO: Add content moderation specific check here
                raise EngineAPIBaseException(
                    message="Bria Engine API failed", route=BriaEngineAPIRoutes.V2_IMAGE_EDIT_REMOVE_BACKGROUND, error_object=e.response.json()
                )

            raise e
