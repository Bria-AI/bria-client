from httpx import Response

from bria_sdk.engine_api.apis.status import StatusAPI
from bria_sdk.engine_api.apis.status_based_api import StatusBasedAPI
from bria_sdk.engine_api.constants import BriaEngineAPIRoutes
from bria_sdk.engine_api.decorators.enable_sync_decorator import enable_run_synchronously
from bria_sdk.engine_api.decorators.wait_for_status_decorator import auto_wait_for_status
from bria_sdk.engine_api.engine_client import BriaEngineClient
from bria_sdk.engine_api.exceptions.engine_api_exception import EngineAPIException
from bria_sdk.engine_api.schemas.image_editing_apis import GetMasksRequestPayload, ObjectEraserRequestPayload, ObjectGenFillRequestPayload


class MasksBasedEditingAPI(StatusBasedAPI):
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        super().__init__(engine_client, status_api)

    @enable_run_synchronously
    @auto_wait_for_status
    async def erase(self, payload: ObjectEraserRequestPayload) -> Response:
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
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_ERASER, payload.payload_dump())
            return response
        except EngineAPIException as e:
            raise BriaEngineClient.get_custom_exception(e, payload)

    @enable_run_synchronously
    @auto_wait_for_status
    async def gen_fill(self, payload: ObjectGenFillRequestPayload) -> Response:
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
            response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_GEN_FILL, payload.payload_dump())
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
        response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V1_IMAGE_EDIT_GET_MASKS, payload.payload_dump())
        if not payload.sync:
            await self._engine_client.file_polling(response.json()["objects_masks"])

        return response
