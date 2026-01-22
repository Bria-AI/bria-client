import logging
from typing import TYPE_CHECKING, Any, NoReturn

from httpx import Response
from pydantic import BaseModel, ConfigDict, Field, model_validator

from bria_client.exceptions import BriaException
from bria_client.toolkit.models import ExcludeNoneBaseModel
from bria_client.toolkit.status import Status

logger = logging.getLogger(__name__)


class BriaResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    if TYPE_CHECKING:
        # Type checkers see this - allows any attribute access
        def __getattr__(self, name: str) -> Any: ...


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
    @classmethod
    def _prepare_model(cls, data: Any) -> Any:
        status = Status.UNKNOWN
        if data.get("error") is not None:
            status = Status.FAILED
        elif data.get("result") is not None:
            status = Status.COMPLETED
        elif data.get("status_url") is not None:
            status = Status.RUNNING
        data["status"] = data.get("status", status)
        return data

    def __str__(self) -> str:
        # The reason for is to exclude none from str
        return f"<{self.__class__.__name__} {self.model_dump()}>"

    def __repr__(self) -> str:
        # The reason for is to exclude none from repr
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
