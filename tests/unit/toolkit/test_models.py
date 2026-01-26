import pytest

from bria_client.toolkit.models import BriaResponse, BriaResult
from bria_client.toolkit.status import Status


@pytest.mark.unit
class TestModels:
    @pytest.mark.parametrize("exclude_none", [True, False])
    def test_bria_response_on_model_dump_should_always_exclude_none_values(self, exclude_none):
        # Arrange
        model = BriaResponse(request_id="1", status=Status.COMPLETED, result=BriaResult.model_construct(b="fake"), error=None)
        # Act
        dump_response = model.model_dump(exclude_none=exclude_none)
        # Assert
        assert dump_response == {"request_id": "1", "result": {"b": "fake"}, "status": "COMPLETED"}
