from httpx import Response

from bria_internal.common.bria_engine_api.constants import BriaEngineAPIRoutes
from bria_internal.common.bria_engine_api.enable_sync_decorator import enable_run_synchronously
from bria_internal.common.bria_engine_api.engine_client import BriaEngineClient
from bria_internal.common.bria_engine_api.status.status import StatusAPI
from bria_internal.exceptions.engine_api_exception import EngineAPIException
from bria_internal.schemas.image_editing_apis.canvas_editing import GetMasksRequestPayload, ObjectEraserRequestPayload, ObjectGenFillRequestPayload
from bria_internal.schemas.status_api import StatusAPIResponse


class CanvasEditingAPI:
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        self.__engine_client = engine_client
        self.__status_api = status_api

    @enable_run_synchronously
    async def erase(self, payload: ObjectEraserRequestPayload, wait_for_status: bool = False) -> Response | StatusAPIResponse:
        """
        Erase an object from an image using a mask

        Args:
            `payload: ObjectEraserRequestPayload` - The payload for the object eraser request
            `wait_for_status: bool` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_ERASER, payload.model_dump(mode="json"))

            if wait_for_status:
                response_body = response.json()
                response = await self.__status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except EngineAPIException as e:
            raise BriaEngineClient.get_custom_exception(e, payload)

    @enable_run_synchronously
    async def gen_fill(self, payload: ObjectGenFillRequestPayload, wait_for_status: bool = False) -> Response | StatusAPIResponse:
        """
        Generate a fill for the provided image using a mask and a prompt to fill the masked area

        Args:
            `payload: ObjectGenFillRequestPayload` - The payload for the object gen fill request
            `wait_for_status: bool` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        try:
            response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_GEN_FILL, payload.model_dump(mode="json"))

            if wait_for_status:
                response_body = response.json()
                response = await self.__status_api.wait_for_status_request(request_id=response_body["request_id"])

            return response
        except EngineAPIException as e:
            raise BriaEngineClient.get_custom_exception(e, payload)

    @enable_run_synchronously
    async def get_masks(self, payload: GetMasksRequestPayload) -> Response:
        """
        Get all the masks for an image in a package

        Args:
            `payload: GetMasksRequestPayload` - The payload for the get masks request

        Returns:
            `Response` - Response with the masks `.zip` file

        Raises:
            `HTTPStatusError` - In cases error is returned from the API

            `PollingException` - If the file polling fails
        """
        response: Response = await self.__engine_client.post(BriaEngineAPIRoutes.V1_IMAGE_EDIT_GET_MASKS, payload.model_dump(mode="json"))
        if not payload.sync:
            await self.__engine_client.file_polling(response.json()["objects_masks"])

        return response
