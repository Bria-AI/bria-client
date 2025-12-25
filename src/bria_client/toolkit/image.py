import sys

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum

from typing import TypeAlias

import numpy as np
from PIL import Image

ImageSource: TypeAlias = Image.Image | str | np.ndarray


class ImageOutputType(StrEnum):
    PNG = "png"
    JPEG = "jpeg"


class ImageMaskKind(StrEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    AUTOMATIC_FULL = "automatic_full"
