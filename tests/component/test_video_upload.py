from unittest.mock import AsyncMock, MagicMock

import pytest

from bria_client.clients.async_client import BriaAsyncClient
from bria_client.clients.sync_client import BriaSyncClient
from bria_client.toolkit import BriaResponse
from bria_client.toolkit.errors.exception import BriaException
from bria_client.toolkit.models import BriaResult, Status

UPLOAD_URL = "https://storage.example.com/bucket/upload"
UPLOAD_FIELDS = {"key": "uploads/video.mp4", "policy": "abc123", "signature": "sig456"}
FILE_URL = "https://cdn.example.com/uploads/video.mp4"


def _make_upload_bria_response() -> BriaResponse:
    result = BriaResult.model_validate({"upload_url": UPLOAD_URL, "upload_fields": UPLOAD_FIELDS, "file_url": FILE_URL})
    return BriaResponse(status=Status.COMPLETED, request_id="req-upload-1", result=result)


def _mock_sync_upload(mocker, status_code: int = 204, text: str = "") -> MagicMock:
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = MagicMock(status_code=status_code, text=text)
    mocker.patch("bria_client.clients.sync_client.httpx.Client", return_value=mock_client)
    return mock_client


def _mock_async_upload(mocker, status_code: int = 204, text: str = "") -> AsyncMock:
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.post.return_value = MagicMock(status_code=status_code, text=text)
    mocker.patch("bria_client.clients.async_client.httpx.AsyncClient", return_value=mock_client)
    return mock_client


@pytest.fixture
def video_file(tmp_path):
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"fake video content")
    return f


@pytest.mark.component
class TestSyncClientVideoUpload:
    def test_upload(self, mocker, video_file):
        client = BriaSyncClient(base_url="https://test.example.com", api_token="tok")
        mocker.patch.object(client.engine.client, "request", return_value=_make_upload_bria_response())
        mock_upload = _mock_sync_upload(mocker)

        file_url = client.upload(video_file, media_type="video/mp4")

        assert file_url == FILE_URL
        call_kwargs = mock_upload.post.call_args
        assert call_kwargs.args[0] == UPLOAD_URL
        assert "file" in call_kwargs.kwargs["files"]

    def test_upload_raises_not_implemented_for_non_video(self, mocker, video_file):
        client = BriaSyncClient(base_url="https://test.example.com", api_token="tok")

        with pytest.raises(NotImplementedError, match="image/png"):
            client.upload(video_file, media_type="image/png")

    def test_upload_raises_on_failure(self, mocker, video_file):
        client = BriaSyncClient(base_url="https://test.example.com", api_token="tok")
        mocker.patch.object(client.engine.client, "request", return_value=_make_upload_bria_response())
        _mock_sync_upload(mocker, status_code=403, text="Access Denied")

        with pytest.raises(BriaException) as exc_info:
            client.upload(video_file, media_type="video/mp4")
        assert exc_info.value.code == 403


@pytest.mark.component
class TestAsyncClientVideoUpload:
    @pytest.mark.asyncio
    async def test_upload(self, mocker, video_file):
        client = BriaAsyncClient(base_url="https://test.example.com", api_token="tok")
        mocker.patch.object(client.engine.client, "request", return_value=_make_upload_bria_response())
        mock_upload = _mock_async_upload(mocker)

        file_url = await client.upload(video_file, media_type="video/mp4")

        assert file_url == FILE_URL
        call_kwargs = mock_upload.post.call_args
        assert call_kwargs.args[0] == UPLOAD_URL
        assert "file" in call_kwargs.kwargs["files"]
