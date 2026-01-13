import logging

from dotenv import load_dotenv

from bria_client import BriaSyncClient
from bria_client.toolkit.image import Image

load_dotenv()

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)


def success_client_use():
    client = BriaSyncClient()

    resp = client.run(
        endpoint="image/edit/remove_background",
        payload={"image": Image("https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png").as_bria_api_input},
    )
    return resp


resp = success_client_use()
print(resp)
