from pydantic import ConfigDict

from bria_client.responses import BriaResponse, BriaResult


class StatusResult(BriaResult):
    model_config = ConfigDict(extra="allow")


class StatusResponse(BriaResponse[StatusResult]):
    pass
