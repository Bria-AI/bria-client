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

    @pytest.mark.parametrize("endpoint", ["/v2/test/endpoint", "v2/test/endpoint", "test/endpoint", "/test/endpoint"])
    def test_prepare_endpoint_removes_v2_refs_from_entered_endpoint_to_keep_it_valid(self, endpoint, api_engine):
        # Arrange
        correct_endpoint = "/v2/test/endpoint"
        # Act
        result = api_engine._prepare_endpoint(endpoint)
        # Assert
        assert result == correct_endpoint
