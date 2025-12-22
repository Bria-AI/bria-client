from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.v2_api import V2API
from bria_client.responses.status_response import StatusResponse


class StatusAPI(V2API):
    path = ""

    @api_endpoint("status")
    def get_status(self, request_id: str):
        response = self.api_engine.get(f"{self.url}/{request_id}", response_obj=StatusResponse)
        return response
