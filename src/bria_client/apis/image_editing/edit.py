from httpx import Response

from bria_client.apis.status import StatusAPI
from bria_client.apis.status_based_api import StatusBasedAPI
from bria_client.constants import BriaEngineAPIRoutes
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.decorators.wait_for_status_decorator import auto_wait_for_status
from bria_client.engine_client import BriaEngineClient
from bria_client.schemas.image_editing_apis.edit import EditRequestPayload
from bria_client.schemas.prompts.sturcture import GenerateStructuredInstructionRequestPayload


class EditAPI(StatusBasedAPI):
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        super().__init__(engine_client, status_api)

    @enable_run_synchronously
    @auto_wait_for_status
    async def edit(self, payload: EditRequestPayload) -> Response:
        """
        Edit the image using the Fibo Edit API

        Args:
            `payload: EditRequestPayload` - The payload for the edit request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT, payload.payload_dump())
        return response

    @enable_run_synchronously
    @auto_wait_for_status
    async def generate_structured_instruction(self, payload: GenerateStructuredInstructionRequestPayload) -> Response:
        """
        Generate a structured instruction for the edit request

        Args:
            `payload: GenerateStructuredInstructionRequestPayload` - The payload for the generate structured instruction request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response: Response = await self._engine_client.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_GENERATE_STRUCTURED_INSTRUCTION, payload.payload_dump())
        return response
