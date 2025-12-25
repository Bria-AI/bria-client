from pydantic import ConfigDict

from bria_client.results import BriaResult


class StatusResult(BriaResult):
    model_config = ConfigDict(extra="allow")
