from __future__ import annotations

import time
from typing import Generic, NoReturn, TypeVar

from httpx import Response
from pydantic import BaseModel, ConfigDict, Field
from pydantic.generics import GenericModel

from bria_client import BriaClient
from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.exceptions.bria_exception import BriaException
from bria_client.schemas import StatusAPIState

T = TypeVar("T", bound="BriaResponse")
R = TypeVar("R", bound="BriaResult")


class BriaResult(BaseModel):
    model_config = ConfigDict(extra="allow")


class BriaError(BaseModel):
    code: int
    message: str
    details: str

    def raise_as_error(self) -> NoReturn:
        raise BriaException.from_error(code=self.code, message=self.message, details=self.details)


class BriaResponse(GenericModel, Generic[R]):
    status: StatusAPIState = Field(default=StatusAPIState.IN_PROGRESS)
    result: R | None = None
    error: BriaError | None = None
    request_id: str
    status_url: str | None = Field(default=None, exclude=True)

    @classmethod
    def from_http_response(cls, response: Response):
        return cls(**response.json())

    def raise_for_status(self) -> NoReturn | None:
        if self.error is not None:
            raise self.error.raise_as_error()

    def in_progress(self) -> bool:
        return self.status is StatusAPIState.IN_PROGRESS

    @enable_run_synchronously
    async def wait_for_status(self, client: BriaClient, raise_on_error: bool = False, interval: float = 0.5, timeout: int = 60) -> BriaResponse:
        start_time = time.time()
        response = None
        while time.time() - start_time <= timeout:
            time.sleep(interval)
            response = await client.status.get_status(request_id=self.request_id)
            if raise_on_error:
                response.raise_for_status()
            if not response.in_progress():
                break

        if response is None:
            raise TimeoutError("Timeout reached while waiting for status request")
        return response
