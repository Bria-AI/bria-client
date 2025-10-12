from enum import Enum


class PollingException(Exception):
    pass


class PollingFileStatus(str, Enum):
    ZERO_BYTE_IMAGE_ERROR = "Zero Byte Image Error"
    INVALID_URL_ERROR = "Invalid URL Error"
    TIMEOUT_ERROR = "Timeout Error"
