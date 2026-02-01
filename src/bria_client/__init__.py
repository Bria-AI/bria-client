import importlib.metadata

from bria_client.clients import BriaAsyncClient, BriaSyncClient

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0"


__all__ = ["BriaSyncClient", "BriaAsyncClient"]
