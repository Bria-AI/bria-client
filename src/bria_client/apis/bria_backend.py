from bria_client.apis.v2 import ImageEditingAPI, StatusAPI
from bria_client.engines import ApiEngine


class BriaBackend:
    def __init__(self, engine: ApiEngine):
        self._engine = engine
        self.status = StatusAPI(self._engine)
        self.image_editing = ImageEditingAPI(api_engine=self._engine)
