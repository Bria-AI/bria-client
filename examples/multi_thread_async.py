import asyncio
import logging

from dotenv import load_dotenv

load_dotenv()

from bria_client import BriaAsyncClient
from bria_client.toolkit import Image

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)


async def request_and_poll():
    aclient = BriaAsyncClient()

    async def request_with_polling():
        response = await aclient.submit(
            endpoint="image/edit/remove_background",
            payload={"image": Image("https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png").as_bria_api_input},
        )
        actual_response = await aclient.poll(response=response)
        return actual_response

    r1, r2 = await asyncio.gather(request_with_polling(), request_with_polling())
    if r1.result:
        print(r1.result.image_url)
    if r2.result:
        print(r2.result.image_url)
    return r1, r2


if __name__ == "__main__":
    asyncio.run(request_and_poll())
