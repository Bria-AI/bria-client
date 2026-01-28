import sys

# noinspection PyUnreachableCode
if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum

import logging
from typing import TYPE_CHECKING, Any, NoReturn

from pydantic import BaseModel, ConfigDict

from bria_client.toolkit import BriaException

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


class Status(StrEnum):
    UNKNOWN = "UNKNOWN"
    FAILED = "ERROR"
    COMPLETED = "COMPLETED"
    RUNNING = "IN_PROGRESS"
