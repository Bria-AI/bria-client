from bria_client.apis.image_editing import ImageEditingAPI
from bria_client.apis.status import StatusAPI
from bria_client.engines.base import ApiEngine


class BriaBackend:
    def __init__(self, engine: ApiEngine):
        self._engine = engine
        self.status = StatusAPI(self._engine)
        self.image_editing = ImageEditingAPI(self._engine, self.status)
