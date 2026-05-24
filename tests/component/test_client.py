import pytest

from bria_client.clients.async_client import BriaAsyncClient
from bria_client.clients.sync_client import BriaSyncClient
from bria_client.toolkit import BriaResponse
from bria_client.toolkit.models import BriaResult, Status


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


@pytest.mark.component
class TestAsyncClientWebhook:
    @pytest.mark.asyncio
    async def test_submit_includes_webhook_url_in_payload(self, mocker):
        # Arrange
        client = BriaAsyncClient(base_url="https://test.example.com", api_token="default_token")
        mock_response = BriaResponse(status=Status.RUNNING, request_id="test_789", result=None)
        mock_post = mocker.patch.object(client.engine.client, "request", return_value=mock_response)

        # Act
        await client.submit(
            endpoint="/test/endpoint",
            payload={"test": "data"},
            webhook_url="https://my-server.example.com/webhook",
        )

        # Assert
        mock_post.assert_called_once()
        payload_sent = mock_post.call_args.kwargs["payload"]
        assert payload_sent["webhook_url"] == "https://my-server.example.com/webhook"
        assert payload_sent["sync"] is False

    @pytest.mark.asyncio
    async def test_submit_without_webhook_url_omits_field(self, mocker):
        # Arrange
        client = BriaAsyncClient(base_url="https://test.example.com", api_token="default_token")
        mock_response = BriaResponse(status=Status.RUNNING, request_id="test_000", result=None)
        mock_post = mocker.patch.object(client.engine.client, "request", return_value=mock_response)

        # Act
        await client.submit(endpoint="/test/endpoint", payload={"test": "data"})

        # Assert
        mock_post.assert_called_once()
        payload_sent = mock_post.call_args.kwargs["payload"]
        assert "webhook_url" not in payload_sent

    @pytest.mark.asyncio
    async def test_submit_preserves_webhook_url_from_payload(self, mocker):
        client = BriaAsyncClient(base_url="https://test.example.com", api_token="default_token")
        mock_response = BriaResponse(status=Status.RUNNING, request_id="test_222", result=None)
        mock_post = mocker.patch.object(client.engine.client, "request", return_value=mock_response)

        await client.submit(
            endpoint="/test/endpoint",
            payload={"test": "data", "webhook_url": "https://my-server.example.com/webhook"},
        )

        mock_post.assert_called_once()
        payload_sent = mock_post.call_args.kwargs["payload"]
        assert payload_sent["webhook_url"] == "https://my-server.example.com/webhook"

    @pytest.mark.asyncio
    async def test_submit_does_not_mutate_original_payload(self, mocker):
        # Arrange
        client = BriaAsyncClient(base_url="https://test.example.com", api_token="default_token")
        mock_response = BriaResponse(status=Status.RUNNING, request_id="test_111", result=None)
        mocker.patch.object(client.engine.client, "request", return_value=mock_response)
        original_payload = {"test": "data"}

        # Act
        await client.submit(
            endpoint="/test/endpoint",
            payload=original_payload,
            webhook_url="https://my-server.example.com/webhook",
        )

        # Assert
        assert "webhook_url" not in original_payload
        assert "sync" not in original_payload
