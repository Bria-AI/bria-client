from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.v2_api import V2API
from bria_client.results.status import StatusResult


class StatusAPI(V2API):
    path = "status"

    @api_endpoint(":request_id")
    def get_status(self, request_id: str):
        """
        Args:
            request_id: is used inside the api_endpoint decorator
        """
        response = self.api_engine.get(self.url, result_obj=StatusResult)
        return response
