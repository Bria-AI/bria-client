from functools import wraps
from urllib.parse import urljoin

from bria_client.engines import ApiEngine


class APIBase:
    path: str = ""
    _parts = []

    def __init__(self, api_engine: ApiEngine):
        for cls in reversed(self.__class__.mro()):
            segment = getattr(cls, "path", None)
            if segment:
                self._parts.append(segment.strip("/"))
        self.api_engine = api_engine
        self.url = self.api_engine.base_url.rstrip("/") + "/" + "/".join(self._parts) + "/"


def api_endpoint(endpoint: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            original_url = self.url
            self.url = urljoin(self.url + "/", endpoint)
            try:
                return func(self, *args, **kwargs)
            finally:
                # ALWAYS restore url to base layer, even if error happens
                self.url = original_url

        return wrapper

    return decorator
