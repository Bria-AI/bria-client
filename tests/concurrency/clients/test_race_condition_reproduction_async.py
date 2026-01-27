"""
Test to reliably reproduce the race condition in BriaEngine._api_token handling (async).

This test uses synchronization primitives and explicit delays to force the race
condition to occur by ensuring multiple async tasks modify self._api_token simultaneously.

The race condition occurs because:
1. Multiple async tasks read self._api_token and store it in old_token
2. Multiple async tasks then modify self._api_token simultaneously
3. When a task calls super().post_async(), it reads self._api_token via auth_headers
4. But another task may have overwritten it, causing the wrong token to be used
"""

import asyncio

import pytest

from bria_client.clients import BriaAsyncClient
from bria_client.engines.bria_engine import BriaEngine
from bria_client.toolkit.models import BriaResponse, BriaResult
from bria_client.toolkit.status import Status


def create_post_async_with_delays(original_post_async):
    """
    Create an async post method with explicit delays to force context switches.

    The delays are placed at critical points:
    - After reading old_token (allows other tasks to interfere)
    - After setting new token but before using it (allows overwrites)
    """

    async def post_async_with_delays(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs) -> BriaResponse:
        """Async post method with delays to force race condition"""
        api_token = kwargs.pop("api_token", self._api_token)
        old_token = self._api_token

        # CRITICAL: Add delay after reading old_token but before setting new token
        # This allows other tasks to interfere
        await asyncio.sleep(0.001)

        try:
            self._api_token = api_token

            # CRITICAL: Add delay after setting token but before using it
            # This is where another task can overwrite it
            await asyncio.sleep(0.01)

            # Now call super().post_async() which will use auth_headers
            return await original_post_async(self, endpoint=endpoint, payload=payload, headers=headers, **kwargs)
        finally:
            self._api_token = old_token

    return post_async_with_delays


def create_header_capture_mock_async(tokens_in_http_headers, headers_lock):
    """
    Create an async mock HTTP request function that captures the token sent in headers.

    Returns:
        Async function that can be used as side_effect for mocker.patch.object
    """

    async def mock_request_async(url, method=None, payload=None, headers=None, **kwargs):
        """Capture the actual token sent in HTTP headers"""
        token_in_headers = headers.get("api_token") if headers else None
        task_id = payload.get("task_id") if payload else None

        if task_id is not None and token_in_headers:
            async with headers_lock:
                tokens_in_http_headers[task_id] = token_in_headers

        return BriaResponse(status=Status.COMPLETED, request_id="test_123", result=BriaResult())

    return mock_request_async


def analyze_race_conditions_async(expected_tokens, tokens_in_http_headers, num_tasks):
    """
    Analyze the results to detect race conditions in async context.

    Returns:
        List of issues where tasks used wrong tokens
    """
    issues = []
    for task_id in range(num_tasks):
        expected = expected_tokens[task_id]
        actual = tokens_in_http_headers.get(task_id)

        if actual and actual != expected:
            issues.append({"task_id": task_id, "expected": expected, "actual_in_http_headers": actual})

    return issues


def format_race_condition_error_async(issues):
    """
    Format a detailed error message when race conditions are detected in async context.
    """
    error_msg = (
        f"RACE CONDITION REPRODUCED! {len(issues)} task(s) sent wrong tokens in HTTP headers:\n"
        + "\n".join(
            [
                f"  Task {i['task_id']}: expected '{i['expected']}', but HTTP request sent '{i['actual_in_http_headers']}'"
                for i in issues[:10]  # Show first 10 to avoid too much output
            ]
        )
        + (f"\n  ... and {len(issues) - 10} more tasks" if len(issues) > 10 else "")
        + "\n\nThis definitively proves that self._api_token in BriaEngine is NOT async-safe!"
        + "\nThe bug occurs because multiple async tasks modify the shared self._api_token"
        + "\ninstance variable simultaneously without synchronization."
    )
    return error_msg


def create_async_barrier(num_tasks):
    """
    Create an async barrier that waits for all tasks to be ready before proceeding.

    Returns:
        Async function that tasks can await to synchronize
    """
    ready_count = 0
    ready_lock = asyncio.Lock()
    start_event = asyncio.Event()

    async def barrier_wait():
        """Wait for all tasks to be ready, then proceed together"""
        nonlocal ready_count
        async with ready_lock:
            ready_count += 1
            if ready_count == num_tasks:
                start_event.set()

        # Wait for all tasks to be ready
        await start_event.wait()

    return barrier_wait


async def run_concurrent_async_tasks(num_tasks, client, barrier_wait, expected_tokens):
    """
    Start multiple async tasks that make requests concurrently.

    Args:
        num_tasks: Number of concurrent tasks to run
        client: BriaAsyncClient instance
        barrier_wait: Async barrier function for synchronization
        expected_tokens: Dictionary to track expected tokens per task

    Returns:
        List of completed tasks
    """

    async def make_request(task_id: int, api_token: str):
        """Make a request with a specific token"""
        expected_tokens[task_id] = api_token

        # All tasks wait here, then proceed together
        await barrier_wait()

        # This is where the race condition occurs
        await client.run(endpoint="/test", payload={"task_id": task_id}, api_token=api_token)

    tasks = []
    for i in range(num_tasks):
        api_token = f"token_{i}"
        task = make_request(i, api_token)
        tasks.append(task)

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

    return tasks


@pytest.mark.concurrency
@pytest.mark.asyncio
async def test_reproduce_race_condition_async_guaranteed(mocker):
    """
    This test reproduces the race condition in async context by patching the engine's
    post_async method to add explicit delays in the critical section, forcing context switches.

    The race happens when multiple async tasks modify self._api_token simultaneously:
    1. Task A: old_token = self._api_token (reads "default")
    2. Task B: old_token = self._api_token (reads "default")
    3. Task A: self._api_token = "token_A"
    4. Task B: self._api_token = "token_B" (overwrites A!)
    5. Task A: super().post_async() -> prepare_headers() -> auth_headers -> reads "token_B"

    This test is designed to FAIL, demonstrating the bug.
    """
    # Setup
    default_token = "default_token"
    client = BriaAsyncClient(base_url="https://test.example.com", api_token=default_token)
    num_tasks = 5

    # Track what token is actually sent in HTTP headers
    tokens_in_http_headers = {}
    headers_lock = asyncio.Lock()
    expected_tokens = {}

    # Patch BriaEngine.post_async to add delays (mocker automatically restores)
    original_post_async = BriaEngine.post_async
    post_with_delays = create_post_async_with_delays(original_post_async)
    mocker.patch.object(BriaEngine, "post_async", post_with_delays)

    try:
        # Mock HTTP client to capture headers
        mock_request_async = create_header_capture_mock_async(tokens_in_http_headers, headers_lock)
        mocker.patch.object(client.engine.client, "request", side_effect=mock_request_async)

        # Setup synchronization
        barrier_wait = create_async_barrier(num_tasks)

        # Run concurrent requests
        await run_concurrent_async_tasks(num_tasks, client, barrier_wait, expected_tokens)

        # Analyze results
        issues = analyze_race_conditions_async(expected_tokens, tokens_in_http_headers, num_tasks)

        # Report race conditions
        if issues:
            error_msg = format_race_condition_error_async(issues)
            print(f"\n{'=' * 80}\n{error_msg}\n{'=' * 80}\n")
            pytest.fail(error_msg)

        # Verify all tasks made requests
        assert len(tokens_in_http_headers) == num_tasks, f"Expected {num_tasks} requests, got {len(tokens_in_http_headers)}"
    finally:
        # Close async client
        await client.aclose()
