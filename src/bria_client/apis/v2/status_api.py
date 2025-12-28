from collections.abc import Awaitable
from typing import TypeVar

from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.v2_api import V2API
from bria_client.results import BriaResponse, BriaResult

T = TypeVar("T", bound=BriaResult)


class StatusAPI(V2API):
    path = "status"

    @api_endpoint(":request_id")
    def get_status(self, request_id: str, result_obj: type[T] = BriaResult) -> Awaitable[BriaResponse[T]] | BriaResponse[T]:
        """
        Args:
            request_id: is used inside the api_endpoint decorator
        """
        response = self.api_engine.get(self.url, result_obj=result_obj)
        return response
