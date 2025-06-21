import pickle
from typing import Any, List, Optional

from redis import Redis

from bria_internal.common.singleton_meta import SingletonABCMeta

DEFAULT_TTL = 3600


class RedisBaseClient(metaclass=SingletonABCMeta):
    def __init__(self, host: str, port: int = 6379):
        assert host is not None, "redis host cannot be None"
        self.client = Redis(host=host, port=port, socket_timeout=10)

    def _get_key(self, key: str) -> str:
        return key

    def set(self, key: str, value: Any, ttl: Optional[int] = DEFAULT_TTL):
        key = self._get_key(key)
        self.client.set(key, self.__serialize(value), ex=ttl)
        return key

    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(self._get_key(key))
        if data is not None:
            return self.__deserialize(data)
        return None

    def get_keys(self, wildcard: Optional[str] = None) -> List[str]:
        if wildcard is None:
            wildcard = ""
        return list(self.client.scan_iter(match=f"*{wildcard}*"))

    @staticmethod
    def __serialize(value: Any) -> bytes:
        return pickle.dumps(value)

    @staticmethod
    def __deserialize(data: bytes) -> Any:
        return pickle.loads(data)
