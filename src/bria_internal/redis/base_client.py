import pickle
from typing import Any, List, Optional

from redis import Redis

from bria_internal.common.singleton_meta import SingletonABCMeta

DEFAULT_TTL = 3600


class RedisBaseClient(metaclass=SingletonABCMeta):
    def __init__(self, host: str, port: int = 6379, key_suffix: Optional[str] = None):
        assert host is not None, "redis host cannot be None"
        self.client = Redis(host=host, port=port, socket_timeout=10)
        assert self.client.ping(), f"redis connection failed for {self.__class__.__name__}"
        self._key_suffix = key_suffix

    def _get_cache_key(self, cache_key: str):
        return f"{cache_key}_{self._key_suffix}" if self._key_suffix else cache_key

    def set(self, key: str, value: Any, ttl: Optional[int] = DEFAULT_TTL):
        self.client.set(self._get_cache_key(key), self.__serialize(value), ex=ttl)
        return self._get_cache_key(key)

    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(self._get_cache_key(key))
        if data is not None:
            return self.__deserialize(data)
        return None

    def delete(self, key: str):
        return self.client.delete(self._get_cache_key(key))

    def get_keys(self, wildcard: Optional[str] = None) -> List[str]:
        if wildcard is None:
            wildcard = ""
        return [key.decode() for key in self.client.scan_iter(match=f"*{wildcard}*")]

    def mget(self, cache_keys: List[str]):
        cache_keys = [self._get_cache_key(k) for k in cache_keys]
        cache_data = self.client.mget(cache_keys)
        return [pickle.loads(data) if data is not None else None for data in cache_data] if cache_data else None

    def delete_pattern(self, key_pattern: str) -> None:
        pattern = self._get_cache_key(key_pattern)
        keys_to_delete = list(self.client.scan_iter(match=pattern))
        if keys_to_delete:
            self.client.delete(*keys_to_delete)

    def get_key_ttl(self, key: str):
        return self.client.ttl(self._get_cache_key(key))

    @staticmethod
    def __serialize(value: Any) -> bytes:
        return pickle.dumps(value)

    @staticmethod
    def __deserialize(data: bytes) -> Any:
        return pickle.loads(data)
