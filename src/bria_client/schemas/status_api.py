from enum import Enum

from pydantic import ConfigDict

from bria_client.exceptions.status_exception import InProgressException, StatusAPIException, SyncAPIException
from bria_client.exceptions.unkown_status_exception import UnknownStatusException
from bria_client.schemas.base_models import APIPayloadModel


class StatusAPIState(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


# TODO: Distribute the result body to the appropriate schemas for each API response
class StatusAPIResultBody(APIPayloadModel):
    model_config = ConfigDict(extra="allow")

    image_url: str | None = None
    video_url: str | None = None
    mask_url: str | None = None
    seed: int | None = None
    prompt: str | None = None
    refined_prompt: str | None = None
    structured_prompt: str | None = None
    structured_instruction: str | None = None


class StatusAPIErrorBody(APIPayloadModel):
    code: int
    message: str
    details: str


class SyncAPIResponse(APIPayloadModel):
    request_id: str
    result: StatusAPIResultBody | None = None
    error: StatusAPIErrorBody | None = None
    warning: str | None = None

    def get_result(self) -> StatusAPIResultBody:
        """
        Get the result nested object if exists

        Returns:
            `StatusAPIResultBody` - The object status when ready

        Raises:
            `APIException` - When the result is not found
        """
        if self.result:
            return self.result
        raise SyncAPIException(**self.error)


class StatusAPIResponse(SyncAPIResponse):
    status: StatusAPIState

    http_request_status: int | None = None

    def get_result(self) -> StatusAPIResultBody:
        """
        Get the result nested object if exists

        Returns:
            `StatusAPIResultBody` - The object status when ready

        Raises:
            `InProgressException` - When status is not ready yet

            `StatusAPIException` - When status is failed with an error

            `UnknownStatusException` - When trying to access before the status is ready, "Status is not ready yet"
        """
        if self.status == StatusAPIState.IN_PROGRESS:
            raise InProgressException("Status is not ready yet")

        if self.status == StatusAPIState.UNKNOWN:
            raise UnknownStatusException("Status is unknown", self)

        if self.error:
            raise StatusAPIException(code=self.error.code, message=self.error.message, details=self.error.details)

        return self.result
