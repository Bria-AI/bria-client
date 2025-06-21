import pytest
from fakeredis import FakeRedis

from bria_internal.redis.base_client import RedisBaseClient


class FakeRedisClient(RedisBaseClient):

    def __init__(self):
        super().__init__(host="localhost", port=6379)

class TestRedisClient:

    @pytest.fixture
    def fake_redis(self, mocker):
        fake = FakeRedis()
        mocker.patch("bria_internal.redis.base_client.Redis", return_value=fake)

    @pytest.fixture
    def fake_client(self, fake_redis):
        return FakeRedisClient()

    def test_client_is_singleton_on_multiple_init_should_call_init_once(self, fake_redis, mocker):
        # Arrange
        RedisBaseClient._instances = {}
        client1 = FakeRedisClient()
        # Act
        client2 = FakeRedisClient()
        # Assert
        assert client1 is client2


    def test_get_on_non_existing_key_should_return_none(self, fake_client):
        # Arrange
        # Act
        data = fake_client.get("non_existing_key")
        # Assert
        assert data is None