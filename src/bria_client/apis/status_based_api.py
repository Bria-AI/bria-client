from bria_client.apis.status import StatusAPI
from bria_client.engine_client import BriaEngineClient


class StatusBasedAPI:
    def __init__(self, engine_client: BriaEngineClient, status_api: StatusAPI):
        self._engine_client = engine_client
        self._status_api = status_api
