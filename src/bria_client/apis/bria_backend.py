import logging
import time
from abc import ABC, abstractmethod

from bria_client.apis.v2 import ImageEditingAPI, StatusAPI
from bria_client.apis.v2.video.video_editing import VideoEditingAPI
from bria_client.apis.v2.video.video_segmenting import VideoSegmentingAPI
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.engines import ApiEngine
from bria_client.results import BriaResponse

logger = logging.getLogger(__name__)


class BriaBackend(ABC):
    def __init__(self):
        self.status = StatusAPI(self._engine)
        self.image_editing = ImageEditingAPI(api_engine=self._engine)
        self.video_editing = VideoEditingAPI(api_engine=self._engine)
        self.video_segmenting = VideoSegmentingAPI(api_engine=self._engine)

    @property
    @abstractmethod
    def _engine(self) -> ApiEngine:
        pass

    @enable_run_synchronously
    async def wait_for_status(self, response: BriaResponse, raise_on_error: bool = False, interval: float = 0.5, timeout: int = 60) -> BriaResponse:
        if response.error is not None:
            if raise_on_error:
                response.raise_for_status()
            raise NotImplementedError("Cannot wait for status when error occurred")

        start_time = time.time()
        response = None
        while time.time() - start_time <= timeout:
            time.sleep(interval)
            logger.debug(f"Polling request status... [{response.request_id}]")
            result_class_R = response.__class__.__pydantic_generic_metadata__["args"][0]
            response = await self.status.get_status(request_id=response.request_id, result_obj=result_class_R)
            if raise_on_error:
                response.raise_for_status()
            if not response.in_progress():
                break

        if response is None:
            raise TimeoutError("Timeout reached while waiting for status request")
        return response
