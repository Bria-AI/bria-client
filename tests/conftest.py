import base64
import io

import numpy as np
import pytest
from PIL import Image

GREEN = [0, 255, 0, 255]
GRAY = [128, 128, 128, 255]


@pytest.fixture
def np_image() -> np.ndarray:
    """200x200 green square image, gray background"""
    input_image_data = np.full((1024, 1024, 4), GREEN, dtype=np.uint8)
    start = (1024 - 200) // 2
    end = start + 200
    input_image_data[start:end, start:end] = GRAY
    return input_image_data


@pytest.fixture
def pil_image(np_image) -> Image.Image:
    return Image.fromarray(np_image)


@pytest.fixture()
def local_image_path(tmp_path, pil_image) -> str:
    pil_image.save(f"{tmp_path}/image.png")
    return f"{tmp_path}/image.png"


@pytest.fixture
def image_url() -> str:
    return "https://www.alleycat.org/wp-content/uploads/2019/03/FELV-cat.jpg"


@pytest.fixture
def base64_image(pil_image) -> str:
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
