from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar
from urllib.parse import urljoin

from bria_client.engines import ApiEngine


class APIBase:
    path: str = ""

    def __init__(self, api_engine: ApiEngine):
        parts = []
        for i, cls in enumerate(reversed(self.__class__.mro())):
            segment = getattr(cls, "path", None)
            if segment:
                parts.append(segment.strip("/"))
        self.api_engine = api_engine
        self.url = self.api_engine.base_url.rstrip("/") + "/" + "/".join(parts) + "/"


# Define type variables to preserve the signature and return type
P = ParamSpec("P")
R = TypeVar("R")


def api_endpoint(endpoint: str):
    """
    Args:
        endpoint: could be static string or ':param' which will take it from the kwargs or try the first arg
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> R:
            actual_endpoint = endpoint
            if endpoint.startswith(":"):
                actual_endpoint = kwargs.get(endpoint[1:])
                if (actual_endpoint is None) and len(args) > 0:
                    # Note: Type checkers might complain about indexing args[0]
                    # with P.args, but for runtime logic this is fine.
                    actual_endpoint = args[0] if args[0] is not None else endpoint

            original_url = self.url
            self.url = urljoin(self.url + "/", str(actual_endpoint))
            try:
                return func(self, *args, **kwargs)
            finally:
                self.url = original_url

        return wrapper  # type: ignore

    return decorator
