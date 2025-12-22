from typing import TypeAlias

import numpy as np
from PIL import Image

ImageSource: TypeAlias = Image.Image | str | np.ndarray
