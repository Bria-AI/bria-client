import logging
import os
from contextvars import ContextVar

from dotenv import load_dotenv

from bria_client.clients.internal_request_client import InternalRequestClient

load_dotenv()

from bria_client.payloads.image_editing_payload import ReplaceBgPayload

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)

api_token_var = ContextVar("api_token", default=os.environ.get("BRIA_API_TOKEN"))

client = InternalRequestClient(base_url="https://engine.prod.bria-api.com", api_token_ctx=api_token_var)
replace_bg_input = ReplaceBgPayload(sync=True, image="https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png", prompt="starry night")

response = client.image_editing.replace_background(payload=replace_bg_input)

print(response.result.image_url)
