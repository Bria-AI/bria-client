from enum import Enum

from pydantic import AnyHttpUrl, BaseModel


class StatusAPIState(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class StatusAPIResultBody(BaseModel):
    image_url: AnyHttpUrl | None = None
    video_url: AnyHttpUrl | None = None
    seed: int | None = None
    prompt: str | None = None
    refined_prompt: str | None = None


class StatusAPIErrorBody(BaseModel):
    code: int
    message: str
    details: str


class StatusAPIResponse(BaseModel):
    request_id: str
    status: StatusAPIState
    result: StatusAPIResultBody | None = None
    error: StatusAPIErrorBody | None = None
