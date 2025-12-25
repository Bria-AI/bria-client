from functools import wraps
from urllib.parse import urljoin


class APIBase:
    path: str = ""

    def __init__(self, api_engine: "ApiEngine"):
        parts = []
        for i, cls in enumerate(reversed(self.__class__.mro())):
            segment = getattr(cls, "path", None)
            if segment:
                parts.append(segment.strip("/"))
        self.api_engine = api_engine
        self.url = self.api_engine.base_url.rstrip("/") + "/" + "/".join(parts) + "/"


def api_endpoint(endpoint: str):
    """
    Args:
        endpoint: could be static string or ':param' which will take it from the kwargs or try the first arg
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            actual_endpoint = endpoint
            if endpoint.startswith(":"):
                actual_endpoint = kwargs.get(endpoint[1:])
                if (actual_endpoint is None) and len(args) > 0:
                    actual_endpoint = args[0]
            original_url = self.url
            self.url = urljoin(self.url + "/", actual_endpoint)
            try:
                return func(self, *args, **kwargs)
            finally:
                # ALWAYS restore url to base layer, even if error happens
                self.url = original_url

        return wrapper

    return decorator
