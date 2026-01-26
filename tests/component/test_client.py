import pytest

from bria_client.clients.sync_client import BriaSyncClient
from bria_client.toolkit.models import BriaResponse, BriaResult
from bria_client.toolkit.status import Status


@pytest.mark.component
class TestClient:
    def test_run_works_ok(self, mocker):
        # Arrange
        client = BriaSyncClient(base_url="https://test.example.com", api_token="default_token")
        test_api_token = "test_override_token"

        # Mock the HTTP client's post method
        mock_response = BriaResponse(status=Status.COMPLETED, request_id="test_123", result=BriaResult())
        mock_post = mocker.patch.object(client.engine.client, "request", return_value=mock_response)

        # Act
        client.run(endpoint="/test/endpoint", payload={"test": "data"}, api_token=test_api_token)

        # Assert
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        headers = call_args.kwargs["headers"]
        assert headers["api_token"] == test_api_token

    def test_submit_works_ok(self, mocker):
        """Verify that api_token passed to .submit() is used in the HTTP request header"""
        # Arrange
        client = BriaSyncClient(base_url="https://test.example.com", api_token="default_token")
        test_api_token = "test_override_token"

        # Mock the HTTP client's post method
        mock_response = BriaResponse(status=Status.RUNNING, request_id="test_456", result=None)
        mock_post = mocker.patch.object(client.engine.client, "request", return_value=mock_response)

        # Act
        client.submit(endpoint="/test/endpoint", payload={"test": "data"}, api_token=test_api_token)

        # Assert
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        headers = call_args.kwargs["headers"]
        assert headers["api_token"] == test_api_token
