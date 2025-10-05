from httpx import HTTPStatusError, Response

from bria_internal.common.bria_engine_api import BriaEngineRequest
from bria_internal.common.bria_engine_api.enable_sync_decorator import enable_run_synchronously
from bria_internal.common.bria_engine_api.routes_constants import BriaEngineAPIRoutes
from bria_internal.common.bria_engine_api.status.status import wait_for_status_request
from bria_internal.exceptions.content_moderation import ContentModerationError
from bria_internal.schemas.image_editing_apis.background_remove import BackgroundRemoveRequestPayload
from bria_internal.schemas.status_api import StatusAPIResponse


@enable_run_synchronously
async def remove_background_by_image_url_v2(
    payload: BackgroundRemoveRequestPayload, wait_for_status: bool = False, engine_request_client: BriaEngineRequest | None = None
) -> Response | StatusAPIResponse:
    """
    Remove the background from the image

    Args:
        payload: BackgroundRemoveRequestPayload - The payload for the background remove request
        wait_for_status: bool - Whether to wait for the status request (locally)
        engine_request_client: BriaEngineRequest - The engine request client to use

    Returns:
        dict - httpx.Response from the API,

        if sync returns the result image, else returns the request id

    Raises:
        ContentModerationError: If the content moderation fails (status code 422)
    """
    try:
        engine_request: BriaEngineRequest = engine_request_client or BriaEngineRequest()
        response: Response = await engine_request.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_REMOVE_BACKGROUND, payload.model_dump())
        response_body = response.json()

        if wait_for_status:
            response = await wait_for_status_request(request_id=response_body["request_id"], engine_request_client=engine_request)

        return response
    except HTTPStatusError as e:
        if e.response.status_code == 422:
            raise ContentModerationError(message="Content moderation failed", route=BriaEngineAPIRoutes.V2_IMAGE_EDIT_REMOVE_BACKGROUND, **e.response.json())

        raise e
