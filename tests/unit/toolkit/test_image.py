import pytest
from pydantic import BaseModel

from bria_client.toolkit.image import Image


@pytest.mark.unit
class TestImage:
    @pytest.mark.parametrize("image_source", ["pil_image", "np_image", "local_image_path", "image_url", "base64_image"])
    def test_image_on_init_should_work_for_all_image_source_types(self, image_source, request):
        # Arrange
        image_source = request.getfixturevalue(image_source)
        # Act
        image = Image(image_source)
        # Assert
        assert image.base64 is not None


@pytest.mark.unit
class TestImageSource:
    def test_type_serializer_on_pydantic_model_dump_should_serialize_param_to_base64(self, pil_image):
        # Arrange
        class TestModel(BaseModel):
            image: Image

        # Act
        model = TestModel(image=pil_image)
        dump_response = model.model_dump()
        # Assert
        assert Image.is_base64(dump_response["image"])
