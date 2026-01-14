import json
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

import httpx

from bria_client.apis.status_based_api import StatusBasedAPI
from bria_client.schemas.status_api import StatusAPIResponse

P = ParamSpec("P")
T = TypeVar("T")


def auto_wait_for_status(
    func: Callable[Concatenate[StatusBasedAPI, P], Awaitable[httpx.Response]] | None = None,
    *,
    timeout: int | None = None,
    interval: int | None = None,
) -> Callable[Concatenate[StatusBasedAPI, P], Awaitable[httpx.Response | StatusAPIResponse]]:
    # TODO: Find the correct type hinting for showing the `wait_for_status` parameter
    """
    Decorator for `StatusBasedAPI` async methods that automatically waits for the
    backend job to reach a terminal status using the Status API.

    Important: This decorator can be assigned only to functions that return
    Status API compatible objects.

    Args:
        func: An async method of a `StatusBasedAPI` subclass that initiates a
            request and returns an `httpx.Response` containing a `request_id` in
            its JSON body.

        timeout: The timeout in seconds to wait for the status request (default: 120)
        interval: The interval in seconds to wait between status requests (default: 2)

    Returns:
        `StatusAPIResponse` - When `wait_for_status=True` (default)

        `httpx.Response` - When `wait_for_status=False`

    Raises:
        `ValueError` - If the decorator is applied to a function that is not a method of a `StatusBasedAPI` instance.
    """

    def decorator(
        f: Callable[Concatenate[StatusBasedAPI, P], Awaitable[httpx.Response]],
    ) -> Callable[Concatenate[StatusBasedAPI, P], Awaitable[httpx.Response | StatusAPIResponse]]:
        @wraps(f)
        async def wrapper(self, *args: P.args, wait_for_status: bool = True, **kwargs: P.kwargs) -> httpx.Response | StatusAPIResponse:
            if not isinstance(self, StatusBasedAPI):
                raise ValueError("This method is not available for this API")

            if not wait_for_status:
                return await f(self, *args, **kwargs)

            response = await f(self, *args, **kwargs)
            if isinstance(response, httpx.Response):
                res_body: dict = response.json()
                request_body: dict = json.loads(response.request.content)
                if not bool(request_body.get("sync")):
                    response = await self._status_api.wait_for_status_request(res_body["request_id"], timeout=timeout, interval=interval)

            return response

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator
