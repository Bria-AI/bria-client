from unittest.mock import patch

import httpx
import pytest

from bria_client.engines.base.sync_http_request import SyncHTTPRequest
from bria_client.toolkit.custom_errors import ServerConnectionError
from bria_client.toolkit.models import Status


@pytest.mark.unit
class TestSyncHTTPRequest:
    def test_request_on_connect_error_should_return_server_connection_error(self):
        # Arrange
        http_request = SyncHTTPRequest()
        # Act
        with patch.object(http_request, "_request", side_effect=httpx.ConnectError("nodename nor servname provided")):
            result = http_request.request(url="https://bad-host.example.com/v1/test", method="POST")
        # Assert
        assert result.status == Status.FAILED.value
        assert isinstance(result.error, ServerConnectionError)
