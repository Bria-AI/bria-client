



import pickle
from abc import ABC, abstractmethod
from typing import Any, Optional

from redis import Redis

from bria_internal.common.singleton_meta import SingletonABCMeta

DEFAULT_TTL = 3600


class RedisBaseClient(metaclass=SingletonABCMeta):

    def __init__(self, host: str, port: int = 6379):
        assert host is not None, "redis host cannot be None"
        self.client = Redis(host=host, port=port, socket_timeout=10)

    def _get_key(self, key: str) -> str:
        return key

    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL):
        self.client.set(self._get_key(key), self.__serialize(value), ex=ttl)

    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(self._get_key(key))
        if data is not None:
            return self.__deserialize(data)
        return None

    def __serialize(self, value: Any) -> bytes:
        return pickle.dumps(value)

    def __deserialize(self, data: bytes) -> Any:
        return pickle.loads(data)
