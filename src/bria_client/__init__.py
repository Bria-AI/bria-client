import importlib.metadata

from bria_client.clients.bria_client import BriaClient

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"


__all__ = ["BriaClient"]
