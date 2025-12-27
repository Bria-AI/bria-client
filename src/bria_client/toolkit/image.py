import base64
import io
import sys

from pydantic import PlainSerializer

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum

from typing import Annotated, TypeAlias

import numpy as np
from PIL import Image as PilImage


class ImageOutputType(StrEnum):
    PNG = "png"
    JPEG = "jpeg"


class ImageMaskKind(StrEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    AUTOMATIC_FULL = "automatic_full"


ImageSource: TypeAlias = Annotated[
    PilImage.Image | str | np.ndarray,
    PlainSerializer(lambda v: Image(v).base64, return_type=str),
]


class Image:
    def __init__(self, image: ImageSource) -> None:
        self._base64: str = self._to_base64(image)

    @property
    def base64(self) -> str:
        return self._base64

    def __str__(self) -> str:
        return self._base64

    @staticmethod
    def _to_base64(image: ImageSource) -> str:
        if isinstance(image, str):
            if Image.is_base64(image):
                return image
            if image.startswith("http"):
                raise NotImplementedError("image url")
                return image
            # infer it as local path
            raise NotImplementedError("local path")
            return image

        if isinstance(image, PilImage.Image):
            buffer = io.BytesIO()
            image.save(buffer, format=image.format or "PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

        if isinstance(image, np.ndarray):
            pil_image = PilImage.fromarray(image)
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

        raise TypeError(f"Unsupported ImageSource: {type(image)!r}")

    @staticmethod
    def is_base64(image: str) -> bool:
        raise NotImplementedError
