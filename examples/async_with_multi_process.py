import asyncio
import logging
import multiprocessing

from dotenv import load_dotenv

from bria_client.toolkit.image import Image

load_dotenv()

from bria_client.clients.bria_clients import BriaAsyncClient

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)

aclient = BriaAsyncClient(base_url="https://engine.prod.bria-api.com")


async def request_and_poll():
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
    return r1, r2


def pool_worker(_):
    return asyncio.run(request_and_poll())


if __name__ == "__main__":
    with multiprocessing.Pool(processes=3) as pool:
        results = pool.map(pool_worker, range(3))
    x = 1
