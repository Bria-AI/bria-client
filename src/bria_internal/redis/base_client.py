



import pickle
from typing import Any, Optional

from redis import Redis

from src.bria_internal.common.singleton_meta import SingletonMeta

DEFAULT_TTL = 3600


class RedisBaseClient(metaclass=SingletonMeta):

    def __init__(self, host: str, port: int = 6379):
        assert host is not None, "redis host cannot be None"
        self.client = Redis(host=host, port=port, socket_timeout=10)

    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL):
        self.client.set(key, self.__serialize(value), ex=ttl)

    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(key)
        if data is not None:
            return self.__deserialize(data)
        return None

    def __serialize(self, value: Any) -> bytes:
        return pickle.dumps(value)

    def __deserialize(self, data: bytes) -> Any:
        return pickle.loads(data)
