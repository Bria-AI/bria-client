import pytest

from bria_client.engines.api_engine import ApiEngine


@pytest.mark.unit
class TestApiEngine:
    def test_prepare_payload_drops_none_values(self):
        payload = {"image_url": "http://example.com/img.png", "mask": None, "seed": None}
        result = ApiEngine._prepare_payload(payload)
        assert result == {"image_url": "http://example.com/img.png"}

    def test_prepare_payload_keeps_all_non_none_values(self):
        payload = {"image_url": "http://example.com/img.png", "seed": 42, "flag": False, "name": ""}
        result = ApiEngine._prepare_payload(payload)
        assert result == payload

    def test_prepare_payload_returns_none_when_payload_is_none(self):
        assert ApiEngine._prepare_payload(None) is None

    def test_prepare_payload_returns_empty_dict_when_all_values_are_none(self):
        result = ApiEngine._prepare_payload({"a": None, "b": None})
        assert result == {}
