import asyncio
import logging
import uuid

import httpx
import pytest

from bria_client import BriaClient
from bria_client.exceptions import BriaException
from bria_client.responses.status import StatusResponse
from bria_client.toolkit.status import Status

logging.basicConfig(level=logging.DEBUG)


class TestStatusApi:
    @pytest.fixture
    def fake_client(self):
        def get_client(handler) -> BriaClient:
            client = BriaClient(base_url="http://localhost:5000", api_token="fake")
            transport = httpx.MockTransport(handler)
            client._engine.transport = transport
            return client

        return get_client

    def test_status_api_get_status_on_return_bria_response(self, fake_client):
        # Arrange
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"error": {"code": 400, "message": "Error message here", "details": "Error details here"}, "status": "ERROR", "request_id": "fake"},
                request=request,
            )

        client = fake_client(handler)
        # Act
        response = client.status.get_status(request_id="fake")
        # Assert
        assert isinstance(response, StatusResponse)

    def test_status_api_get_status_on_raise_for_status_should_raise_BriaException(self, fake_client):
        # Arrange
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"error": {"code": 400, "message": "Error message here", "details": "Error details here"}, "status": "ERROR", "request_id": "fake"},
                request=request,
            )

        client = fake_client(handler)
        # Act
        response = client.status.get_status(request_id="fake")
        with pytest.raises(BriaException):
            # Assert
            response.raise_for_status()

    @pytest.mark.asyncio
    async def test_status_api_get_status_on_async_return_bria_response(self, fake_client):
        # Arrange
        async def handler(request: httpx.Request) -> httpx.Response:
            await asyncio.sleep(0.1)
            request_id = request.url.path.rpartition("/")[-1]
            if request_id == "1":
                return httpx.Response(
                    200,
                    json={"result": {"correct": "good"}, "status": Status.COMPLETED, "request_id": request_id},
                    request=request,
                )
            return httpx.Response(
                200,
                json={
                    "error": {"code": 400, "message": "Error message here", "details": "Error details here"},
                    "status": Status.ERROR,
                    "request_id": request_id,
                },
                request=request,
            )

        client = fake_client(handler)
        # Act
        r1, r2 = await asyncio.gather(client.status.get_status(request_id="1"), client.status.get_status(request_id="2"))
        try:
            r1.raise_for_status()
        except BriaException:
            pytest.fail("request 1 should be succesfull")
        with pytest.raises(BriaException):
            r2.raise_for_status()

    @pytest.mark.asyncio
    def test_status_api_get_status_on_wait_for_status_should_poll_until_result(self, fake_client):
        # Arrange
        request_counter = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal request_counter
            request_counter += 1
            if request_counter == 5:
                return httpx.Response(200, json={"status": "COMPLETED", "result": {"correct": "good"}, "request_id": "done"}, request=request)
            return httpx.Response(
                200,
                json={"status": "IN_PROGRESS", "request_id": uuid.uuid4().hex},
                request=request,
            )

        client = fake_client(handler)
        # Act
        response = client.status.get_status(request_id="fake")
        actual_response = response.wait_for_status(client)
        assert actual_response.result.correct == "good"
