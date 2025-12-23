from abc import ABC, abstractmethod

from bria_client.apis.v2 import ImageEditingAPI, StatusAPI
from bria_client.engines import ApiEngine


class BriaBackend(ABC):
    def __init__(self):
        self.status = StatusAPI(self._engine)
        self.image_editing = ImageEditingAPI(api_engine=self._engine)

    @abstractmethod
    @property
    def _engine(self) -> ApiEngine:
        pass
