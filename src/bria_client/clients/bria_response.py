import logging
from typing import NoReturn

from httpx import Response
from pydantic import BaseModel, ConfigDict, Field, model_validator

from bria_client.exceptions import BriaException
from bria_client.toolkit.models import ExcludeNoneBaseModel
from bria_client.toolkit.status import Status

logger = logging.getLogger(__name__)


class BriaResult(BaseModel):
    model_config = ConfigDict(extra="allow")


class BriaError(BaseModel):
    code: int
    message: str
    details: str

    def throw(self) -> NoReturn:
        raise BriaException.from_error(code=self.code, message=self.message, details=self.details)


class BriaResponse(ExcludeNoneBaseModel):
    model_config = ConfigDict(use_enum_values=True)

    request_id: str
    status: Status
    error: BriaError | None = Field(default=None)
    result: BriaResult | None = Field(default=None)
    status_url: str | None = Field(default=None)

    @model_validator(mode="before")
    def _prepare_model(self):
        status = Status.UNKNOWN
        if self.get("error") is not None:
            status = Status.FAILED
        elif self.get("result") is not None:
            status = Status.COMPLETED
        elif self.get("status_url") is not None:
            status = Status.RUNNING
        self["status"] = self.get("status", status)
        return self

    def __str__(self) -> str:
        # reason for is to exclude none from str
        return f"<{self.__class__.__name__} {self.model_dump()}>"

    def __repr__(self) -> str:
        # reason for is to exclude none from repr
        return f"<{self.__class__.__name__} {self.model_dump()}>"

    @classmethod
    def from_http_response(cls, response: Response):
        return cls(**response.json())

    def raise_for_status(self) -> NoReturn | None:
        if self.error is not None:
            raise self.error.throw()

    @property
    def in_progress(self) -> bool:
        return self.status is Status.RUNNING.value
