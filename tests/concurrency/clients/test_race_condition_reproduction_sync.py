"""
Test to reliably reproduce the race condition in BriaEngine._api_token handling (sync/threading).

This test uses synchronization primitives and explicit delays to force the race
condition to occur by ensuring multiple threads modify self._api_token simultaneously.

The race condition occurs because:
1. Multiple threads read self._api_token and store it in old_token
2. Multiple threads then modify self._api_token simultaneously
3. When a thread calls super().post(), it reads self._api_token via auth_headers
4. But another thread may have overwritten it, causing the wrong token to be used
"""

import threading
import time

import pytest

from bria_client.clients import BriaSyncClient
from bria_client.engines.bria_engine import BriaEngine
from bria_client.toolkit.models import BriaResponse, BriaResult
from bria_client.toolkit.status import Status


def create_post_with_delays(original_post):
    """
    Create a post method with explicit delays to force context switches.

    The delays are placed at critical points:
    - After reading old_token (allows other threads to interfere)
    - After setting new token but before using it (allows overwrites)
    """

    def post_with_delays(self, endpoint: str, payload: dict, headers: dict | None = None, **kwargs) -> BriaResponse:
        """Post method with delays to force race condition"""
        api_token = kwargs.pop("api_token", self._api_token)
        old_token = self._api_token

        # CRITICAL: Add delay after reading old_token but before setting new token
        # This allows other threads to interfere
        time.sleep(0.001)

        try:
            self._api_token = api_token

            # CRITICAL: Add delay after setting token but before using it
            # This is where another thread can overwrite it
            time.sleep(0.01)

            # Now call super().post() which will use auth_headers
            return original_post(self, endpoint=endpoint, payload=payload, headers=headers, **kwargs)
        finally:
            self._api_token = old_token

    return post_with_delays


def create_header_capture_mock(tokens_in_http_headers, headers_lock):
    """
    Create a mock HTTP request function that captures the token sent in headers.

    Returns:
        Function that can be used as side_effect for mocker.patch.object
    """

    def mock_request(url, method=None, payload=None, headers=None, **kwargs):
        """Capture the actual token sent in HTTP headers"""
        token_in_headers = headers.get("api_token") if headers else None
        thread_id = payload.get("thread_id") if payload else None

        if thread_id is not None and token_in_headers:
            with headers_lock:
                tokens_in_http_headers[thread_id] = token_in_headers

        return BriaResponse(status=Status.COMPLETED, request_id="test_123", result=BriaResult())

    return mock_request


def run_concurrent_requests(num_threads, client, start_barrier, expected_tokens):
    """
    Start multiple threads that make requests concurrently.

    Args:
        num_threads: Number of threads to create
        client: BriaSyncClient instance
        start_barrier: Threading barrier for synchronization
        expected_tokens: Dictionary to track expected tokens per thread

    Returns:
        List of thread objects
    """

    def make_request(thread_id: int, api_token: str):
        """Make a request with a specific token"""
        expected_tokens[thread_id] = api_token

        # All threads wait here, then proceed together
        start_barrier.wait()

        # This is where the race condition occurs
        client.run(endpoint="/test", payload={"thread_id": thread_id}, api_token=api_token)

    threads = []
    for i in range(num_threads):
        api_token = f"token_{i}"
        thread = threading.Thread(target=make_request, args=(i, api_token))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return threads


def analyze_race_conditions(expected_tokens, tokens_in_http_headers, num_threads):
    """
    Analyze the results to detect race conditions.

    Returns:
        List of issues where threads used wrong tokens
    """
    issues = []
    for thread_id in range(num_threads):
        expected = expected_tokens[thread_id]
        actual = tokens_in_http_headers.get(thread_id)

        if actual and actual != expected:
            issues.append({"thread_id": thread_id, "expected": expected, "actual_in_http_headers": actual})

    return issues


def format_race_condition_error(issues):
    """
    Format a detailed error message when race conditions are detected.
    """
    error_msg = (
        f"RACE CONDITION REPRODUCED! {len(issues)} thread(s) sent wrong tokens in HTTP headers:\n"
        + "\n".join(
            [
                f"  Thread {i['thread_id']}: expected '{i['expected']}', but HTTP request sent '{i['actual_in_http_headers']}'"
                for i in issues[:10]  # Show first 10 to avoid too much output
            ]
        )
        + (f"\n  ... and {len(issues) - 10} more threads" if len(issues) > 10 else "")
        + "\n\nThis definitively proves that self._api_token in BriaEngine is NOT thread-safe!"
        + "\nThe bug occurs because multiple threads modify the shared self._api_token"
        + "\ninstance variable simultaneously without synchronization."
    )
    return error_msg


@pytest.mark.concurrency
def test_reproduce_race_condition(mocker):
    """
    This test reproduces the race condition by patching the engine's post method
    to add explicit delays in the critical section, forcing context switches.

    The race happens when multiple threads modify self._api_token simultaneously:
    1. Thread A: old_token = self._api_token (reads "default")
    2. Thread B: old_token = self._api_token (reads "default")
    3. Thread A: self._api_token = "token_A"
    4. Thread B: self._api_token = "token_B" (overwrites A!)
    5. Thread A: super().post() -> prepare_headers() -> auth_headers -> reads "token_B"

    This test is designed to FAIL, demonstrating the bug.
    """
    # Setup
    default_token = "default_token"
    client = BriaSyncClient(base_url="https://test.example.com", api_token=default_token)
    num_threads = 5

    # Track what token is actually sent in HTTP headers
    tokens_in_http_headers = {}
    headers_lock = threading.Lock()
    expected_tokens = {}

    # Patch BriaEngine.post to add delays (mocker automatically restores)
    original_post = BriaEngine.post
    post_with_delays = create_post_with_delays(original_post)
    mocker.patch.object(BriaEngine, "post", post_with_delays)

    # Mock HTTP client to capture headers
    mock_request = create_header_capture_mock(tokens_in_http_headers, headers_lock)
    mocker.patch.object(client.engine.client, "request", side_effect=mock_request)

    # Setup synchronization
    start_barrier = threading.Barrier(num_threads)

    # Run concurrent requests
    run_concurrent_requests(num_threads, client, start_barrier, expected_tokens)

    # Analyze results
    issues = analyze_race_conditions(expected_tokens, tokens_in_http_headers, num_threads)

    # Report race conditions
    if issues:
        error_msg = format_race_condition_error(issues)
        print(f"\n{'=' * 80}\n{error_msg}\n{'=' * 80}\n")
        pytest.fail(error_msg)

    # Verify all threads made requests
    assert len(tokens_in_http_headers) == num_threads, f"Expected {num_threads} requests, got {len(tokens_in_http_headers)}"
