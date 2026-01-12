import logging

from dotenv import load_dotenv

from bria_client import BriaSyncClient

load_dotenv()

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)


def success_client_use():
    client = BriaSyncClient(base_url="https://engine.prod.bria-api.com")
    resp = client.run(endpoint="image/edit/remove_background", payload={"image": "https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png"})
    return resp


resp = success_client_use()
