import asyncio
import time
from typing import Awaitable

from httpx import Response

from bria_internal.common.bria_engine_api import BriaEngineRequest
from bria_internal.common.bria_engine_api.enable_sync_decorator import enable_run_synchronously
from bria_internal.common.bria_engine_api.routes_constants import BriaEngineAPIRoutes
from bria_internal.schemas.status_api import StatusAPIResponse, StatusAPIState


@enable_run_synchronously
async def wait_for_status_request(
    request_id: str, engine_request_client: BriaEngineRequest = None, timeout: int = 120, interval: int = 2
) -> Awaitable[StatusAPIResponse] | StatusAPIResponse:
    if not request_id or not engine_request_client:
        raise ValueError("Request ID and engine_request_client are required")

    start_time = time.time()
    while time.time() - start_time < timeout:
        res: Response = await engine_request_client.get(f"{BriaEngineAPIRoutes.V2_STATUS}/{request_id}")
        data: dict = res.json()

        status_response: StatusAPIResponse = StatusAPIResponse(**data)
        if status_response.status != StatusAPIState.IN_PROGRESS.value:
            return status_response

        await asyncio.sleep(interval)

    raise TimeoutError("Timeout reached while waiting for status request")
