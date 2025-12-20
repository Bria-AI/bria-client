from bria_client.apis import ImageEditingAPI, StatusAPI
from bria_client.apis.v2.image.image_editing import ImageEditingAPI as V2ImageEditingAPI
from bria_client.engines.base import ApiEngine


class BriaBackend:
    def __init__(self, engine: ApiEngine):
        self._engine = engine
        self.status = StatusAPI(self._engine)
        self.also_image_editing = V2ImageEditingAPI(api_engine=self._engine)
        self.image_editing = ImageEditingAPI(self._engine, self.status)
