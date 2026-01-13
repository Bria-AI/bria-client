import sys
from pathlib import Path

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum

import base64
import binascii
import io
from typing import TypeAlias

import numpy as np
import requests
from PIL import Image as PilImage
from PIL import UnidentifiedImageError
from pydantic import AnyHttpUrl
from pydantic_core import core_schema


class ImageOutputType(StrEnum):
    PNG = "png"
    JPEG = "jpeg"


Base64String: TypeAlias = str
LocalPath: TypeAlias = str | Path

ImageSource: TypeAlias = PilImage.Image | AnyHttpUrl | np.ndarray | Base64String | LocalPath


class Image:
    def __init__(self, image: ImageSource) -> None:
        self._base64_or_url: str = self._safely_process_image(image)

    @property
    def as_bria_api_input(self) -> str:
        return self._base64_or_url

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return core_schema.no_info_plain_validator_function(
            lambda v: v if isinstance(v, cls) else cls(v),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: v.as_bria_api_input,
                return_schema=core_schema.str_schema(),
            ),
        )

    def _safely_process_image(self, image: ImageSource) -> Base64String | str:
        try:
            return self._process_image(image)
        except Exception as e:
            raise ValueError(f"Failed to process image: {image!r}") from e

    def _process_image(self, image: ImageSource) -> Base64String | str:
        if isinstance(image, str):
            if Image.is_base64(image):
                return image
            if image.startswith("http"):
                return image
            # infer it is a local path
            pil_image = PilImage.open(image)
            return self._pil_2_b64(pil_image)
        if isinstance(image, Path):
            pil_image = PilImage.open(str(image))
            return self._pil_2_b64(pil_image)
        if isinstance(image, AnyHttpUrl):
            return str(image)
        if isinstance(image, PilImage.Image):
            return self._pil_2_b64(image)
        if isinstance(image, np.ndarray):
            pil_image = PilImage.fromarray(image)
            return self._pil_2_b64(pil_image)

        raise TypeError(f"Unsupported ImageSource: {type(image)!r}")

    @staticmethod
    def is_base64(image: str) -> bool:
        try:
            base64.b64decode(image, validate=True)
            return True
        except (binascii.Error, UnidentifiedImageError, OSError):
            return False

    def _pil_2_b64(self, image: PilImage.Image) -> Base64String:
        buffer = io.BytesIO()
        image.save(buffer, format=image.format or "PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _url_2_pil(self, image_url: str) -> PilImage.Image:
        with requests.get(image_url, stream=True, timeout=10) as response:
            response.raise_for_status()
            chunks = [chunk for chunk in response.iter_content(chunk_size=8192) if chunk]
            img_bytes = b"".join(chunks)
        pil_image = PilImage.open(io.BytesIO(img_bytes))
        pil_image.load()
        return pil_image
