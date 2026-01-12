from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def with_temp_api_token(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator that temporarily swaps the instance's _api_token if an api_token
    parameter is provided in the method call.

    The original token is always restored after the method execution,
    even if an exception occurs.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> R:
        api_token = kwargs.pop("api_token", self._api_token)
        old_token = self._api_token
        try:
            self._api_token = api_token
            return func(self, *args, **kwargs)
        finally:
            self._api_token = old_token

    return wrapper
