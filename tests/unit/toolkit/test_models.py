import pytest

from bria_client.toolkit.models import ExcludeNoneBaseModel


@pytest.mark.unit
class TestModels:
    @pytest.mark.parametrize("exclude_none", [True, False])
    def test_ExcludeNoneBaseModel_on_model_dump_should_always_exclude_none_values(self, exclude_none):
        # Arrange
        class TestModel(ExcludeNoneBaseModel):
            a: str | None = None
            b: str = "fake"

        model = TestModel()
        # Act
        dump_response = model.model_dump(exclude_none=exclude_none)
        # Assert
        assert "a" not in dump_response
        assert "b" in dump_response
