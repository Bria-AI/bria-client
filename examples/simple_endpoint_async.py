import logging
import os

from dotenv import load_dotenv

load_dotenv()

from bria_client.payloads.image_editing import ReplaceBackgroundRequestPayload

from bria_client import BriaClient

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)


client = BriaClient(base_url="https://engine.prod.bria-api.com", api_token=os.environ.get("BRIA_API_TOKEN"))

replace_bg_input = ReplaceBackgroundRequestPayload(
    sync=False, image="https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png", prompt="starry night"
)

response = client.image_editing.replace_background(payload=replace_bg_input)
actual_response = response.wait_for_status(client=client)

print(actual_response.result.image_url)
