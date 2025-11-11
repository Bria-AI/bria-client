from bria_client.apis.status import StatusAPI
from bria_client.clients.engine_client import EngineClient


class StatusBasedAPI:
    def __init__(self, engine_client: EngineClient, status_api: StatusAPI):
        self._engine_client = engine_client
        self._status_api = status_api
