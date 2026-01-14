from bria_client.apis.image.generation import ImageGenerationAPI
from bria_client.apis.status import StatusAPI
from bria_client.engine_client import BriaEngineClient


class ImageAPI:
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        self.generation = ImageGenerationAPI(engine_client, status_api)
