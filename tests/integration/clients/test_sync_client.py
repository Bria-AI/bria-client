from unittest.mock import patch

import pytest

from bria_client.clients.bria_clients import BriaSyncClient
from bria_client.clients.bria_response import BriaResponse
from bria_client.toolkit.status import Status


@pytest.mark.integration
class TestSyncClientApiToken:
    """Test that api_token kwarg is properly passed to HTTP headers"""

    def test_run_with_api_token_kwarg_uses_token_in_header(self):
        # Arrange
        client = BriaSyncClient(base_url="https://test.example.com", api_token="default_token")
        test_api_token = "test_override_token"

        # Mock the HTTP client's post method
        mock_response = BriaResponse(status=Status.COMPLETED, request_id="test_123", result=None)
        with patch.object(client.engine.client, "post", return_value=mock_response) as mock_post:
            # Act
            client.run(endpoint="/test/endpoint", payload={"test": "data"}, api_token=test_api_token)

            # Assert
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert headers["api_token"] == test_api_token

    def test_submit_with_api_token_kwarg_uses_token_in_header(self):
        # Arrange
        client = BriaSyncClient(base_url="https://test.example.com", api_token="default_token")
        test_api_token = "test_override_token"

        # Mock the HTTP client's post method
        mock_response = BriaResponse(status=Status.RUNNING, request_id="test_456", result=None)
        with patch.object(client.engine.client, "post", return_value=mock_response) as mock_post:
            # Act
            client.submit(endpoint="/test/endpoint", payload={"test": "data"}, api_token=test_api_token)

            # Assert
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert headers["api_token"] == test_api_token

    def test_run_without_api_token_kwarg_uses_default_token(self):
        """Verify that without api_token kwarg, the default token is used"""
        # Arrange
        default_token = "default_token"
        client = BriaSyncClient(base_url="https://test.example.com", api_token=default_token)

        # Mock the HTTP client's post method
        mock_response = BriaResponse(status=Status.COMPLETED, request_id="test_789", result={"data": "test"})
        with patch.object(client.engine.client, "post", return_value=mock_response) as mock_post:
            # Act
            client.run(endpoint="/test/endpoint", payload={"test": "data"})

            # Assert
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert headers["api_token"] == default_token
