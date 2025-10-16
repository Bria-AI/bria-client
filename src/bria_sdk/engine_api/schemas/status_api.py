from enum import Enum

from pydantic import AnyHttpUrl

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