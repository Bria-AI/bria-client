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
    client = BriaSyncClient()

    resp = client.submit(
        endpoint="video/segment/mask_by_prompt",
        payload={"video": "https://bria-test-images.s3.us-east-1.amazonaws.com/videos/eraser_mask/woman_right_side.mov", "prompt": "women"},
    )

    actual_resp = client.poll(request_id=resp.request_id, interval=1, timeout=300)
    return actual_resp


resp = polling_client_use()
print(resp)
