import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def pil_image() -> Image.Image:
    return ""


@pytest.fixture
def np_image() -> np.ndarray:
    return ""


@pytest.fixture
def local_image_path() -> str:
    # mock the load of this thing globally
    return ""


@pytest.fixture
def image_url() -> str:
    # mock the load of this thing globally
    return ""


@pytest.fixture
def base64_image() -> str:
    return ""
