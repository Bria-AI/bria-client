import logging

from dotenv import load_dotenv

load_dotenv()

from bria_client import BriaSyncClient

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)


def failed_client_use():
    client = BriaSyncClient()

    resp = client.run(endpoint="image/edit/remove_background", payload={"image": "htts://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png"})
    return resp


response = failed_client_use()
print(response)
response.raise_for_status()
