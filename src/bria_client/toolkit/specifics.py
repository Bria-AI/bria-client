import sys

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum


class GenFillVersion(StrEnum):
    V1 = "1"
    V2 = "2"


class IncreaseResDesiredIncrease(StrEnum):
    TIMES_2X = "2"
    TIMES_4X = "4"


class ReplaceBackgroundMode(StrEnum):
    BASE = "base"
    FAST = "fast"
    HIGH_CONTROL = "high_control"
