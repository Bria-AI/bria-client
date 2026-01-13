import asyncio
import logging

from dotenv import load_dotenv

from bria_client.toolkit.image import Image

load_dotenv()

from bria_client.clients.bria_clients import BriaAsyncClient

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)


async def request_and_poll():
    aclient = BriaAsyncClient(base_url="https://engine.prod.bria-api.com")

    async def request_with_polling():
        response = await aclient.submit(
            endpoint="image/edit/remove_background",
            payload={"image": Image("https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png").as_bria_api_input},
        )
        actual_response = await aclient.poll(response=response)
        return actual_response

    r1, r2 = await asyncio.gather(request_with_polling(), request_with_polling())
    print(r1.result.image_url)
    print(r2.result.image_url)
    return r1, r2


if __name__ == "__main__":
    asyncio.run(request_and_poll())
