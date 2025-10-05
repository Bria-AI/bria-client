import base64
import re

from pydantic import ValidationError


def base64_pre_process(string: str) -> str:
    """
    Removes the data URL prefix from the base64 string if `string` is base64 string.

    Args:
        base64_str: str - Base64 string to pre-process

    Returns:
        The Base64 string without the data URL prefix

        Else returns the original string
    """
    data_url_pattern = r"^data:image\/[a-zA-Z]+;base64,"
    if re.match(data_url_pattern, string):
        return string.split(",")[1]  # Actual base64 string
    return string


def validate_base64(data: str) -> None:
    """
    Validates if the data is a valid base64 string.

    Args:
        data: str - Data to validate

    Raises:
        ValidationError: If the data is not a valid base64 string
    """
    try:
        base64.b64decode(data)
    except Exception:
        raise ValidationError("Invalid base64 file: file argument should be in base64 format.")


def validate_url_or_base64(data: str) -> None:
    """
    Validates if the data is a valid URL or base64 string.

    Args:
        data: str - Data to validate

    Raises:
        ValidationError: If the data is not a valid URL or base64 string
    """
    if re.match(r"^https?://", data):
        return
    validate_base64(data)
