from enum import Enum

from pydantic import AnyHttpUrl, BaseModel, ValidationError, field_validator, model_validator


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

    @model_validator(mode="after")
    def should_have_url(self):
        if not self.image_url and not self.video_url:
            raise ValidationError("At least one of 'image_url' or 'video_url' must be provided.")
        return self


class StatusAPIErrorBody(BaseModel):
    code: int
    message: str
    details: str


class StatusAPIResponse(BaseModel):
    request_id: str
    status: str
    result: StatusAPIResultBody | None = None
    error: StatusAPIErrorBody | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        if value not in [status.value for status in StatusAPIState]:
            raise ValidationError(f"Invalid status: {value}")
        return value

    @model_validator(mode="after")
    def validate_result(self):
        # If status is COMPLETED, should have result
        if self.status == StatusAPIState.COMPLETED.value and self.result is None:
            raise ValidationError("COMPLETED status requires a result")

        # If status is ERROR, should have error
        if self.status == StatusAPIState.ERROR.value and self.error is None:
            raise ValidationError("ERROR status requires an error")

        return self
