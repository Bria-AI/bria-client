import pytest

from bria_client.clients.bria_response import BriaError, BriaResponse
from bria_client.exceptions import BriaException
from bria_client.toolkit.status import Status


@pytest.mark.integartion
class TestBriaErrorIntegrations:
    def test_error_on_raise_as_error_should_raise_exception_and_keep_fields_values(self):
        # Arrange
        error = BriaError(code=1, message="fake message", details="fake details")
        # Act
        try:
            error.throw()
        except BriaException as e:
            # Assert
            assert e.code == 1
            assert e.message == "fake message"
            assert e.details == "fake details"


@pytest.mark.integartion
class TestBriaResponseIntegrations:
    def test_bria_response_model_dump_on_excluding_none_valued_fields(self):
        # Arrange
        response = BriaResponse(status=Status.COMPLETED, request_id="123", result=None)
        # Act
        dumped_result = response.model_dump()
        # Assert
        assert dumped_result == {"status": "COMPLETED", "request_id": "123"}
