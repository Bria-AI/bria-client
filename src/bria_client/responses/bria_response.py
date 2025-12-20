from typing import NoReturn, TypeVar

from httpx import Response
from pydantic import BaseModel

from bria_client.exceptions.bria_exception import BriaException
from bria_client.schemas import StatusAPIState

T = TypeVar("T", bound="BriaResponse")


class BriaResult(BaseModel):
    pass


class BriaError(BaseModel):
    code: int
    message: str
    details: str

    def raise_as_error(self) -> NoReturn:
        raise BriaException.from_error(code=self.code, message=self.message, details=self.details)


class BriaResponse(BaseModel):
    status: StatusAPIState
    result: BriaResult | None = None
    error: BriaError | None = None
    request_id: str

    @classmethod
    def from_http_response(cls: type[T], response: Response) -> T:
        return cls(**response.json())

    def raise_for_status(self) -> NoReturn | None:
        if self.error is not None:
            raise self.error.raise_as_error()
