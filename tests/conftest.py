import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def np_image() -> np.ndarray:
    return np.array([])


@pytest.fixture
def pil_image(np_image) -> Image.Image:
    return Image.fromarray(np_image)


@pytest.fixture(scope="session")
def local_image_path(tmp_path, pil_image) -> str:
    pil_image.save(f"{tmp_path}/image.png")
    return f"{tmp_path}/image.png"


@pytest.fixture
def image_url() -> str:
    return "https://www.alleycat.org/wp-content/uploads/2019/03/FELV-cat.jpg"


@pytest.fixture
def base64_image() -> str:
    return ""
