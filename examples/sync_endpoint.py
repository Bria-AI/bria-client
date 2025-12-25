import logging

from dotenv import load_dotenv

load_dotenv()

from bria_client import BriaClient
from bria_client.payloads.image_editing_payload import ReplaceBgPayload

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)

client = BriaClient(base_url="https://engine.prod.bria-api.com")
replace_bg_input = ReplaceBgPayload(sync=True, image="https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png", prompt="starry night")

response = client.image_editing.replace_background(payload=replace_bg_input)
print(response.result.image_url)
