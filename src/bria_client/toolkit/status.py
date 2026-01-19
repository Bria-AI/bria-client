import sys

# noinspection PyUnreachableCode
if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum


class Status(StrEnum):
    UNKNOWN = "UNKNOWN"
    FAILED = "ERROR"
    COMPLETED = "COMPLETED"
    RUNNING = "IN_PROGRESS"
