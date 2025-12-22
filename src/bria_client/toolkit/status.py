from enum import Enum


class Status(str, Enum):
    UNKNOWN = "UNKNOWN"
    FAILED = "ERROR"
    COMPLETED = "COMPLETED"
    RUNNING = "IN_PROGRESS"
