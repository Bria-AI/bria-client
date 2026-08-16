import inspect

import pytest

from bria_client import BriaSyncClient
from bria_client._version import __version__
from bria_client.engines.api_engine import ApiEngine
from bria_client.engines.bria_engine import BriaEngine
from bria_client.toolkit import Status, verify_webhook_signature


@pytest.mark.unit
class TestContractParity:
    """Asserts the Python SDK matches the shared repo-root contract/ (see contract/README.md)."""

    def test_status_enum_matches_contract(self, contract_constants):
        # Arrange
        expected = contract_constants["status"]
        # Assert
        assert Status.UNKNOWN.value == expected["UNKNOWN"]
        assert Status.FAILED.value == expected["FAILED"]
        assert Status.COMPLETED.value == expected["COMPLETED"]
        assert Status.RUNNING.value == expected["RUNNING"]

    def test_auth_header_name_matches_contract(self, contract_constants):
        # Arrange
        engine = BriaEngine(base_url="https://x", api_token="tok")
        # Act
        headers = engine._prepare_headers()
        # Assert
        assert headers[contract_constants["authHeaderName"]] == "tok"

    def test_upload_endpoint_matches_contract(self, contract_constants):
        # The client posts uploads to this endpoint (see BriaSyncClient.upload).
        assert contract_constants["endpoints"]["upload"] == "video/upload"

    def test_poll_defaults_match_contract(self, contract_constants):
        # Arrange
        params = inspect.signature(BriaSyncClient.poll).parameters
        # Assert
        assert params["interval"].default == contract_constants["poll"]["defaultIntervalSeconds"]
        assert params["timeout"].default == contract_constants["poll"]["defaultTimeoutSeconds"]

    def test_endpoint_normalization_matches_contract(self, load_contract_fixture):
        # Arrange
        fixture = load_contract_fixture("fixtures/endpoint-normalization.json")
        engine = BriaEngine(base_url=fixture["baseUrl"], api_token="tok")
        # Act / Assert
        for case in fixture["cases"]:
            assert engine._prepare_endpoint(case["input"]) == case["expected"]

    def test_payload_null_stripping_matches_contract(self, load_contract_fixture):
        # Arrange
        fixture = load_contract_fixture("fixtures/payload-null-stripping.json")
        # Act / Assert
        for case in fixture["cases"]:
            assert ApiEngine._prepare_payload(case["input"]) == case["expected"]

    def test_user_agent_matches_contract(self, contract_constants, load_contract_fixture):
        # Arrange
        fixture = load_contract_fixture("fixtures/user-agent.json")
        template = contract_constants["userAgentTemplate"]
        engine = BriaEngine(base_url="https://x", api_token="tok")
        # Assert: template renders as documented, and the engine emits a contract-shaped UA.
        for case in fixture["cases"]:
            rendered = template.replace("{version}", case["version"]).replace("{lang}", case["lang"])
            assert rendered == case["expected"]
        assert engine.user_agent_headers["User-Agent"] == f"BriaSDK/{__version__} (python)"

    def test_webhook_verification_matches_contract(self, load_contract_fixture):
        # Arrange
        fixture = load_contract_fixture("fixtures/webhook.json")
        # Act / Assert
        for case in fixture["cases"]:
            result = verify_webhook_signature(
                payload=case["payload"].encode(),
                webhook_id=case["webhookId"],
                timestamp=case["timestamp"],
                signature_header=case["signatureHeader"],
                api_token=case["apiToken"],
            )
            assert result is case["expected"], case["name"]
