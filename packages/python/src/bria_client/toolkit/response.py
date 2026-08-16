import logging
from typing import Any, NoReturn

from httpx import Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_serializer, model_validator
from pydantic_core.core_schema import SerializationInfo, SerializerFunctionWrapHandler

from bria_client.toolkit.models import BriaError, BriaResult, Status

logger = logging.getLogger(__name__)


class BriaResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    request_id: str = "unknown"
    status: Status
    error: BriaError | None = Field(default=None)
    result: BriaResult | None = Field(default=None)
    status_url: str | None = Field(default=None)
    headers: dict[str, str] = Field(default_factory=dict, exclude=True)

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

    # noinspection PyUnusedLocal
    @model_serializer(mode="wrap")
    def _force_exclude_none(self, handler: SerializerFunctionWrapHandler, info: SerializationInfo) -> dict[str, Any]:
        result = handler(self)
        # force exclude_none=True over BaseModel
        result = {k: v for k, v in result.items() if v is not None}
        return result

    def __str__(self) -> str:
        # The reason for is to exclude none from str
        return f"<{self.__class__.__name__} {self.model_dump()}>"

    def __repr__(self) -> str:
        # The reason for is to exclude none from repr
        return f"<{self.__class__.__name__} {self.model_dump()}>"

    @classmethod
    def from_error(cls, error: BriaError, headers: dict[str, str] | None = None) -> "BriaResponse":
        return cls(status=Status.FAILED, error=error, headers=headers or {})

    @classmethod
    def from_http_response(cls, response: Response) -> "BriaResponse":
        headers = dict(response.headers)
        try:
            if isinstance(response.json(), dict):
                parsed = cls(**response.json(), headers=headers)
            else:
                raise ValueError("Response is not a JSON object")
        except (ValueError, ValidationError):
            logger.debug("Failed to parse response as BriaResponse")
            parsed = None
        if parsed is None or (response.status_code >= 400 and parsed.error is None):
            return cls.from_error(cls._error_from_response(response), headers=headers)
        return parsed

    @staticmethod
    def _error_from_response(response: Response) -> BriaError:
        return BriaError(
            code=response.status_code,
            message=response.reason_phrase or f"HTTP {response.status_code}",
            details=response.text,
        )

    def raise_for_status(self) -> NoReturn | None:
        if self.error is not None:
            raise self.error.throw()

    @property
    def in_progress(self) -> bool:
        return self.status is Status.RUNNING.value
