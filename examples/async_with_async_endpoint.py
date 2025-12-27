import asyncio
import logging
import os

from dotenv import load_dotenv

from bria_client.payloads.image_editing_payload import ReplaceBgPayload

load_dotenv()


from bria_client import BriaClient

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)


async def request_and_poll():
    client = BriaClient(base_url="https://engine.prod.bria-api.com", api_token=os.environ.get("BRIA_API_TOKEN"))

    replace_bg_input = ReplaceBgPayload(sync=False, image="https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png", prompt="starry night")

    async def request_with_polling():
        response = await client.image_editing.replace_background(payload=replace_bg_input)
        actual_response = await client.wait_for_status(response=response)
        return actual_response

    r1, r2 = await asyncio.gather(request_with_polling(), request_with_polling())
    print(r1.result.image_url)
    return r1, r2


if __name__ == "__main__":
    asyncio.run(request_and_poll())
