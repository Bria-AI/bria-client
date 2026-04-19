from unittest.mock import MagicMock

import pytest

from bria_client.toolkit import BriaException, BriaResponse
from bria_client.toolkit.models import BriaError, Status


@pytest.mark.unit
class TestBriaError:
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

    def test_error_response_on_throw_should_raise_as_bria_exception(self):
        # Arrange
        error = BriaError(code=1, message="fake message", details="fake details")
        # Act
        with pytest.raises(BriaException):
            # Assert
            error.throw()


@pytest.mark.unit
class TestBriaResponse:
    def test_bria_response_model_dump_on_excluding_none_valued_fields(self):
        # Arrange
        response = BriaResponse(status=Status.COMPLETED, request_id="123", result=None)
        # Act
        dumped_result = response.model_dump()
        # Assert
        assert dumped_result == {"status": "COMPLETED", "request_id": "123"}

    def test_bria_response_on_no_headers_should_exclude_from_model_dump(self):
        # Arrange
        response = BriaResponse(status=Status.COMPLETED, request_id="123")
        # Act
        dumped_result = response.model_dump()
        # Assert
        assert "headers" not in dumped_result

    def test_bria_response_on_headers_set_should_include_in_model_dump(self):
        # Arrange
        response = BriaResponse(status=Status.COMPLETED, request_id="123", headers={"x-request-id": "abc"})
        # Act
        dumped_result = response.model_dump()
        # Assert
        assert dumped_result["headers"] == {"x-request-id": "abc"}

    def test_from_http_response_should_capture_headers(self):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"request_id": "req-1", "status": "COMPLETED"}
        mock_response.headers = {"content-type": "application/json", "x-request-id": "req-1"}
        # Act
        bria_response = BriaResponse.from_http_response(mock_response)
        # Assert
        assert bria_response.headers == {"content-type": "application/json", "x-request-id": "req-1"}
