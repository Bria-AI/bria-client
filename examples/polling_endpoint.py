import logging

from dotenv import load_dotenv
from httpx_retries import Retry

load_dotenv()

from bria_client import BriaSyncClient


class PlatformSyncClient(BriaSyncClient):
    def __init__(self, base_url: str | None = None, jwt_token: str | None = None, retry: Retry | None = Retry(total=3, backoff_factor=2)):
        self.jwt = jwt_token
        super().__init__(base_url=base_url, api_token=None, retry=retry)

    @property
    def auth_headers(self) -> dict[str, str]:
        return {"jwt_token": self.jwt}


logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)


def polling_client_use():
    client = BriaSyncClient(base_url="https://engine.prod.bria-api.com")

    resp = client.submit(
        endpoint="video/edit/remove_background",
        payload={
            "background_color": "Transparent",
            "output_container_and_codec": "webm_vp9",
            "video": "https://bria-test-images.s3.us-east-1.amazonaws.com/videos/1_min_video.mp4",
        },
    )

    actual_resp = client.poll(request_id=resp.request_id, interval=1, timeout=300)
    return actual_resp


resp = polling_client_use()
print(resp)
