from unittest.mock import MagicMock

import pytest

from bria_client.toolkit import BriaException, BriaResponse
from bria_client.toolkit.custom_errors import EndpointNotFoundError
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
    def test_from_error_should_return_failed_response_with_error(self):
        # Arrange
        error = BriaError(code=503, message="Service Unavailable", details="server down")
        # Act
        result = BriaResponse.from_error(error)
        # Assert
        assert result.status == Status.FAILED.value
        assert result.error is error
        assert result.request_id == "unknown"

    def test_from_http_response_on_404_should_return_endpoint_not_found_error(self):
        # Arrange
        response = MagicMock()
        response.status_code = 404
        response.url = "https://engine.prod.bria.cc/v1/image/edit/remove_backgrund"
        # Act
        result = BriaResponse.from_http_response(response)
        # Assert
        assert result.status == Status.FAILED.value
        assert isinstance(result.error, EndpointNotFoundError)

    def test_from_http_response_on_non_json_body_should_return_structured_error(self):
        # Arrange
        response = MagicMock()
        response.json.side_effect = ValueError("No JSON")
        response.status_code = 500
        response.reason_phrase = "Internal Server Error"
        response.text = "Something went wrong"
        # Act
        result = BriaResponse.from_http_response(response)
        # Assert
        assert result.status == Status.FAILED.value
        assert result.error is not None
        assert result.error.code == 500

    def test_from_http_response_on_error_json_should_return_structured_error(self):
        # Arrange
        response = MagicMock()
        response.json.return_value = {
            "request_id": "abc-123",
            "error": {"code": 502, "message": "Bad Gateway", "details": "upstream failed"},
        }
        # Act
        result = BriaResponse.from_http_response(response)
        # Assert
        assert result.status == Status.FAILED.value
        assert result.error is not None
        assert result.error.code == 502

    def test_from_http_response_on_valid_json_should_parse_normally(self):
        # Arrange
        response = MagicMock()
        response.json.return_value = {"request_id": "abc-123", "result": {"url": "https://example.com"}}
        # Act
        result = BriaResponse.from_http_response(response)
        # Assert
        assert result.status == Status.COMPLETED.value
        assert result.error is None

    def test_bria_response_model_dump_on_excluding_none_valued_fields(self):
        # Arrange
        response = BriaResponse(status=Status.COMPLETED, request_id="123", result=None)
        # Act
        dumped_result = response.model_dump()
        # Assert
        assert dumped_result == {"status": "COMPLETED", "request_id": "123"}
