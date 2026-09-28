import pytest
from pydantic import BaseModel

from bria_client.toolkit import Image


@pytest.mark.unit
class TestImage:
    @pytest.mark.parametrize("image_source", ["pil_image", "np_image", "local_image_path", "image_url", "base64_image"])
    def test_image_on_init_should_work_for_all_image_source_types(self, image_source, request):
        # Arrange
        image_source = request.getfixturevalue(image_source)
        # Act
        image = Image(image_source)
        # Assert
        assert image.as_bria_api_input is not None

    @pytest.mark.parametrize("prefix", ["data:image/png;base64,", "data:image/jpeg;base64,"])
    def test_image_on_init_with_base64_data_uri_should_process_successfully(self, base64_image, prefix):
        # Arrange
        base64_with_header = f"{prefix}{base64_image}"
        # Act
        image = Image(base64_with_header)
        # Assert
        assert Image.is_base64(image.as_bria_api_input)


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
