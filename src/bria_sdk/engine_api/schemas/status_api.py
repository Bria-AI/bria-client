from enum import Enum

from pydantic import AnyHttpUrl

from bria_sdk.engine_api.exceptions.unkown_status import UnknownStatusException
from bria_sdk.engine_api.schemas.base_models import APIPayloadModel


class StatusAPIState(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class StatusAPIResultBody(APIPayloadModel):
    image_url: AnyHttpUrl | None = None
    video_url: AnyHttpUrl | None = None
    seed: int | None = None
    prompt: str | None = None
    refined_prompt: str | None = None


class StatusAPIErrorBody(APIPayloadModel):
    code: int
    message: str
    details: str


class StatusAPIResponse(APIPayloadModel):
    request_id: str
    status: StatusAPIState
    result: StatusAPIResultBody | None = None
    error: StatusAPIErrorBody | None = None

    http_request_status: int | None = None

    def get_result(self) -> StatusAPIResultBody:
        """
        Get the result nested object if exists

        Returns:
            `StatusAPIResultBody` - The object status when ready

        Raises:
            `Exception` - Exception object with the `StatusAPIErrorBody` in it

            `UnknownStatusException` - When trying to access before the status is ready, "Status is not ready yet"
        """
        if self.status == StatusAPIState.IN_PROGRESS:
            raise Exception("Status is not ready yet")

        if self.status == StatusAPIState.UNKNOWN:
            raise UnknownStatusException("Status is unknown", self)

        if self.error:
            raise Exception(self.error)

        return self.result
