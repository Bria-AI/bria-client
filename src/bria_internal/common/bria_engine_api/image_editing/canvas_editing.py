from typing import Awaitable

from httpx import Response

from bria_internal.common.bria_engine_api.constants import BriaEngineAPIRoutes
from bria_internal.common.bria_engine_api.enable_sync_decorator import enable_run_synchronously
from bria_internal.common.bria_engine_api.engine_client import BriaEngineClient
from bria_internal.common.bria_engine_api.status.status import StatusAPI
from bria_internal.schemas.image_editing_apis.canvas_editing import GetMasksRequestPayload, ObjectEraserRequestPayload, ObjectGenFillRequestPayload
from bria_internal.schemas.status_api import StatusAPIResponse


class CanvasEditingAPI:
    def __init__(self, engine_api: BriaEngineClient, status_api: StatusAPI):
        self.engine_api = engine_api
        self.status_api = status_api

    @enable_run_synchronously
    async def erase(self, payload: ObjectEraserRequestPayload, wait_for_status: bool = False) -> Awaitable[Response | StatusAPIResponse]:
        """
        Erase an object from an image using a mask

        Args:
            payload: ObjectEraserRequestPayload

        Returns:
            Response | StatusAPIResponse - StatusAPIResponse if the wait_for_status is True, else returns the Response from the API

        Throws:
            EngineAPIBaseException: In cases error is returned from the API
        """
        response: Response = await self.engine_api.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_ERASER, payload.model_dump())

        if wait_for_status:
            response_body = response.json()
            response = await self.status_api.wait_for_status_request(request_id=response_body["request_id"])

        return response

    @enable_run_synchronously
    async def gen_fill(self, payload: ObjectGenFillRequestPayload, wait_for_status: bool = False) -> Awaitable[Response | StatusAPIResponse]:
        """
        Generate a fill for the provided image using a mask and a prompt to fill the masked area

        Args:
            payload: ObjectGenFillRequestPayload

        Returns:
            Response | StatusAPIResponse - StatusAPIResponse if the wait_for_status is True, else returns the Response from the API

        Throws:
            EngineAPIBaseException: In cases error is returned from the API
        """
        response: Response = await self.engine_api.post(BriaEngineAPIRoutes.V2_IMAGE_EDIT_GEN_FILL, payload.model_dump())

        if wait_for_status:
            response_body = response.json()
            response = await self.status_api.wait_for_status_request(request_id=response_body["request_id"])

        return response

    @enable_run_synchronously
    async def get_masks(self, payload: GetMasksRequestPayload) -> Awaitable[Response]:
        """
        Get all the masks for an image in a package

        Args:
            payload: GetMasksRequestPayload

        Returns:
            Response with the masks `.zip` file

        Throws:
            EngineAPIBaseException: In cases error is returned from the API
        """
        response: Response = await self.engine_api.post(BriaEngineAPIRoutes.V1_IMAGE_EDIT_GET_MASKS, payload.model_dump())
        if not payload.sync:
            await self.engine_api.file_polling(response.json()["objects_masks"])

        return response
