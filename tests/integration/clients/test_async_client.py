import asyncio

import pytest

from bria_client.clients.async_client import BriaAsyncClient
from bria_client.engines.bria_engine import BriaEngine
from bria_client.toolkit import BriaResponse
from bria_client.toolkit.models import BriaResult, Status


@pytest.mark.integration
class TestAsyncClientApiTokenIntegrations:
    """Test that api_token kwarg is properly passed to HTTP headers"""

    @pytest.mark.asyncio
    async def test_run_with_api_token_kwarg_uses_token_in_header(self, mocker):
        """Verify that api_token passed to .run() is used in the HTTP request header"""
        # Arrange
        client = BriaAsyncClient(base_url="https://test.example.com", api_token="default_token")
        test_api_token = "test_override_token"

        # Mock the HTTP client's post_async method
        mock_response = BriaResponse(status=Status.COMPLETED, request_id="test_123", result=BriaResult())
        mock_post = mocker.patch.object(client.engine.client, "request", return_value=mock_response)

        # Act
        await client.run(endpoint="/test/endpoint", payload={"test": "data"}, api_token=test_api_token)

        # Assert
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        headers = call_args.kwargs["headers"]
        assert headers["api_token"] == test_api_token

    @pytest.mark.asyncio
    async def test_submit_with_api_token_kwarg_uses_token_in_header(self, mocker):
        """Verify that api_token passed to .submit() is used in the HTTP request header"""
        # Arrange
        client = BriaAsyncClient(base_url="https://test.example.com", api_token="default_token")
        test_api_token = "test_override_token"

        # Mock the HTTP client's post_async method
        mock_response = BriaResponse(status=Status.RUNNING, request_id="test_456", result=None)
        mock_post = mocker.patch.object(client.engine.client, "request", return_value=mock_response)

        # Act
        await client.submit(endpoint="/test/endpoint", payload={"test": "data"}, api_token=test_api_token)

        # Assert
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        headers = call_args.kwargs["headers"]
        assert headers["api_token"] == test_api_token

    @pytest.mark.asyncio
    async def test_run_without_api_token_kwarg_uses_default_token(self, mocker):
        """Verify that without api_token kwarg, the default token is used"""
        # Arrange
        default_token = "default_token"
        client = BriaAsyncClient(base_url="https://test.example.com", api_token=default_token)

        # Mock the HTTP client's post_async method
        mock_response = BriaResponse(status=Status.COMPLETED, request_id="test_789", result=BriaResult())
        mock_post = mocker.patch.object(client.engine.client, "request", return_value=mock_response)

        # Act
        await client.run(endpoint="/test/endpoint", payload={"test": "data"})

        # Assert
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        headers = call_args.kwargs["headers"]
        assert headers["api_token"] == default_token

    @pytest.mark.asyncio
    async def test_concurrent_tasks_use_correct_api_tokens(self, mocker):
        # Arrange
        client = BriaAsyncClient(base_url="https://test.example.com", api_token="default_token")
        num_tasks = 5
        tokens_in_http_headers = {}
        headers_lock = asyncio.Lock()
        expected_tokens = {}
        ready_count = 0
        ready_lock = asyncio.Lock()
        start_event = asyncio.Event()

        async def post_async_with_delays(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs) -> BriaResponse:
            api_token = kwargs.pop("api_token", self._api_token)
            await asyncio.sleep(0.001)
            auth_override = {"api_token": api_token} if api_token else None
            await asyncio.sleep(0.01)
            return await self.async_request(endpoint=endpoint, method="POST", payload=payload, headers=headers, auth_override=auth_override, **kwargs)

        async def mock_request_async(url, method=None, payload=None, headers=None, **kwargs):
            token_in_headers = headers.get("api_token") if headers else None
            task_id = payload.get("task_id") if payload else None
            if task_id is not None and token_in_headers:
                async with headers_lock:
                    tokens_in_http_headers[task_id] = token_in_headers
            return BriaResponse(status=Status.COMPLETED, request_id="test_123", result=BriaResult())

        async def barrier_wait():
            nonlocal ready_count
            async with ready_lock:
                ready_count += 1
                if ready_count == num_tasks:
                    start_event.set()
            await start_event.wait()

        async def make_request(task_id: int, api_token: str):
            expected_tokens[task_id] = api_token
            await barrier_wait()
            await client.run(endpoint="/test", payload={"task_id": task_id}, api_token=api_token)

        mocker.patch.object(BriaEngine, "post_async", post_async_with_delays)
        mocker.patch.object(client.engine.client, "request", side_effect=mock_request_async)

        # Act
        try:
            tasks = [make_request(i, f"token_{i}") for i in range(num_tasks)]
            await asyncio.gather(*tasks)
        finally:
            await client.aclose()

        # Assert
        for task_id in range(num_tasks):
            expected = expected_tokens[task_id]
            actual = tokens_in_http_headers.get(task_id)
            assert actual == expected, f"Task {task_id}: expected '{expected}', got '{actual}'"
        assert len(tokens_in_http_headers) == num_tasks
