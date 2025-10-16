from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

import httpx

from bria_sdk.engine_api.apis.status_based_api import StatusBasedAPI
from bria_sdk.engine_api.schemas.status_api import StatusAPIResponse

P = ParamSpec("P")
T = TypeVar("T")

def auto_wait_for_status(
    func: Callable[Concatenate[StatusBasedAPI, P], Awaitable[httpx.Response]]
) -> Callable[Concatenate[StatusBasedAPI, P], Awaitable[httpx.Response | StatusAPIResponse]]:
    # TODO: Find the correct type hinting for showing the `wait_for_status` parameter
    @wraps(func)
    async def wrapper(
        self,
        *args: P.args,
        wait_for_status: bool = True,
        **kwargs: P.kwargs,
    ) -> httpx.Response | StatusAPIResponse:
        if not isinstance(self, StatusBasedAPI):
            raise ValueError("This method is not available for this API")

        if not wait_for_status:
            return await func(self, *args, **kwargs)

        response = await func(self, *args, **kwargs)
        if isinstance(response, httpx.Response):
            res_body: dict = response.json()
            response = await self._status_api.wait_for_status_request(
                res_body["request_id"]
            )
        return response

    return wrapper