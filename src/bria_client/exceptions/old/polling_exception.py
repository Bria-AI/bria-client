from enum import Enum


class PollingException(Exception):
    pass


class PollingFileStatus(str, Enum):
    ZERO_BYTE_IMAGE_ERROR = "Zero Byte Image Error"
    TIMEOUT_ERROR = "Timeout Error"
