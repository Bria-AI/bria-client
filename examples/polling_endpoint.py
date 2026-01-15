import logging

from dotenv import load_dotenv

from bria_client import BriaSyncClient

load_dotenv()


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
