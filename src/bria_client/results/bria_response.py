from __future__ import annotations

import logging
import time
from typing import Generic, NoReturn, TypeVar

from httpx import Response
from pydantic import BaseModel, ConfigDict, Field, model_validator

from bria_client.decorators.enable_sync_decorator import enable_run_synchronously
from bria_client.exceptions import BriaException
from bria_client.toolkit.models import ExcludeNoneBaseModel
from bria_client.toolkit.status import Status

T = TypeVar("T", bound="BriaResponse")
R = TypeVar("R", bound="BriaResult")
logger = logging.getLogger(__name__)


class BriaResult(BaseModel):
    model_config = ConfigDict(extra="allow")


class BriaError(BaseModel):
    code: int
    message: str
    details: str

    def raise_as_error(self) -> NoReturn:
        raise BriaException.from_error(code=self.code, message=self.message, details=self.details)


class BriaResponse(ExcludeNoneBaseModel, Generic[R]):
    status: Status = Field(default=Status.RUNNING)
    result: R | None = None
    error: BriaError | None = None
    request_id: str
    status_url: str | None = Field(default=None)

    def __str__(self) -> str:
        # reason for is to exclude none from str
        return f"<{self.__class__.__name__} {self.model_dump()}>"

    def __repr__(self) -> str:
        # reason for is to exclude none from repr
        return f"<{self.__class__.__name__} {self.model_dump()}>"

    @classmethod
    def from_http_response(cls, response: Response):
        response_obj = cls
        if "error" in response.json():

            class BriaErrorResponse(BriaResponse):
                status: Status = Field(default=Status.FAILED)
                pass

            response_obj = BriaErrorResponse
        return response_obj(**response.json())

    @model_validator(mode="after")
    def ensure_status(self):
        if self.error is not None:
            self.status = Status.FAILED
        if self.result is not None:
            self.status = Status.COMPLETED
        return self

    def raise_for_status(self) -> NoReturn | None:
        if self.error is not None:
            raise self.error.raise_as_error()

    def in_progress(self) -> bool:
        return self.status is Status.RUNNING

    @enable_run_synchronously
    async def wait_for_status(self, client: BriaClient, raise_on_error: bool = False, interval: float = 0.5, timeout: int = 60) -> BriaResponse:
        if self.error is not None:
            if raise_on_error:
                self.raise_for_status()
            raise NotImplementedError("Cannot wait for status when error occurred")

        start_time = time.time()
        response = None
        while time.time() - start_time <= timeout:
            time.sleep(interval)
            logger.debug(f"Polling request status... [{self.request_id}]")
            result_class_R = self.__class__.__pydantic_generic_metadata__["args"][0]
            response = await client.status.get_status(request_id=self.request_id, result_obj=result_class_R)
            if raise_on_error:
                response.raise_for_status()
            if not response.in_progress():
                break

        if response is None:
            raise TimeoutError("Timeout reached while waiting for status request")
        return response
