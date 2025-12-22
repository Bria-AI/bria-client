import logging
import os

from dotenv import load_dotenv

from bria_client.exceptions.bria_exception import BriaException

load_dotenv()

from bria_client import BriaClient
from bria_client.schemas.image_editing_apis import RemoveBackgroundRequestPayload

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)


client = BriaClient(base_url="https://engine.prod.bria-api.com", api_token=os.environ.get("BRIA_API_TOKEN"))

replace_bg_input = RemoveBackgroundRequestPayload(sync=True, image="https://invalid_url")
try:
    response = client.image_editing.remove_background(payload=replace_bg_input)
    response.raise_for_status()
except BriaException as e:
    print("############ caught raised response ############")
    print("code: ", e.code)
    print("message: ", e.message)
    print("details: ", e.details)
    print("################################################")
print("\n\n\n\n")
response = client.image_editing.remove_background(payload=replace_bg_input)
print("############ returned error from response ############")
print(repr(response.error))
print("################################################")
