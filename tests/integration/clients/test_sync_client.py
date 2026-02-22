import threading
import time

import pytest

from bria_client.clients import BriaSyncClient
from bria_client.engines.bria_engine import BriaEngine
from bria_client.toolkit import BriaResponse
from bria_client.toolkit.models import BriaResult, Status


@pytest.mark.integration
class TestSyncClientApiTokenIntegrations:
    """Test that api_token kwarg is properly passed to HTTP headers"""

    def test_run_with_api_token_kwarg_uses_token_in_header(self, mocker):
        """Verify that api_token passed to .run() is used in the HTTP request header"""
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

    def test_submit_with_api_token_kwarg_uses_token_in_header(self, mocker):
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

    def test_run_without_api_token_kwarg_uses_default_token(self, mocker):
        """Verify that without api_token kwarg, the default token is used"""
        # Arrange
        default_token = "default_token"
        client = BriaSyncClient(base_url="https://test.example.com", api_token=default_token)

        # Mock the HTTP client's post method
        mock_response = BriaResponse(status=Status.COMPLETED, request_id="test_789", result=BriaResult())
        mock_post = mocker.patch.object(client.engine.client, "request", return_value=mock_response)

        # Act
        client.run(endpoint="/test/endpoint", payload={"test": "data"})

        # Assert
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        headers = call_args.kwargs["headers"]
        assert headers["api_token"] == default_token

    def test_request_includes_user_agent_header(self, mocker):
        """Verify that every request includes the User-Agent header with SDK version"""
        # Arrange
        client = BriaSyncClient(base_url="https://test.example.com", api_token="default_token")
        mock_response = BriaResponse(status=Status.COMPLETED, request_id="test_123", result=BriaResult())
        mock_post = mocker.patch.object(client.engine.client, "request", return_value=mock_response)

        # Act
        client.run(endpoint="/test/endpoint", payload={"test": "data"})

        # Assert
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        headers = call_args.kwargs["headers"]
        assert "User-Agent" in headers
        assert headers["User-Agent"].startswith("BriaSDK/")
        assert headers["User-Agent"].endswith("(python)")

    def test_concurrent_threads_use_correct_api_tokens(self, mocker):
        # Arrange
        client = BriaSyncClient(base_url="https://test.example.com", api_token="default_token")
        num_threads = 5
        tokens_in_http_headers = {}
        headers_lock = threading.Lock()
        expected_tokens = {}
        start_barrier = threading.Barrier(num_threads)

        def post_with_delays(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs) -> BriaResponse:
            api_token = kwargs.pop("api_token", self._api_token)
            time.sleep(0.001)
            auth_override = {"api_token": api_token} if api_token else None
            time.sleep(0.01)
            return self.sync_request(endpoint=endpoint, method="POST", payload=payload, headers=headers, auth_override=auth_override, **kwargs)

        def mock_request(url, method=None, payload=None, headers=None, **kwargs):
            token_in_headers = headers.get("api_token") if headers else None
            thread_id = payload.get("thread_id") if payload else None
            if thread_id is not None and token_in_headers:
                with headers_lock:
                    tokens_in_http_headers[thread_id] = token_in_headers
            return BriaResponse(status=Status.COMPLETED, request_id="test_123", result=BriaResult())

        def make_request(thread_id: int, api_token: str):
            expected_tokens[thread_id] = api_token
            start_barrier.wait()
            client.run(endpoint="/test", payload={"thread_id": thread_id}, api_token=api_token)

        mocker.patch.object(BriaEngine, "post", post_with_delays)
        mocker.patch.object(client.engine.client, "request", side_effect=mock_request)

        # Act
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=make_request, args=(i, f"token_{i}"))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        # Assert
        for thread_id in range(num_threads):
            expected = expected_tokens[thread_id]
            actual = tokens_in_http_headers.get(thread_id)
            assert actual == expected, f"Thread {thread_id}: expected '{expected}', got '{actual}'"
        assert len(tokens_in_http_headers) == num_threads
