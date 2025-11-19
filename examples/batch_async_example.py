# /// script
# requires-python = ">=3.10"
# dependencies = [
# "bria_client@git+https://github.com/Bria-AI/bria-client.git",
# ]
# ///

"""
Example script demonstrating batch async processing of multiple images using asyncio tasks.
This example shows how to process multiple images concurrently for better performance.
"""

import asyncio
from bria_client import BriaClient
from bria_client.schemas.image_editing_apis.size_editing import ExpandImageRequestPayload
from bria_client.schemas.status_api import StatusAPIResultBody



async def process_single_image(client: BriaClient, image_url: str, index: int) -> dict:
    try:
        print(f"Processing image {index + 1}: {image_url}")
        response = await client.image_editing.expand_image(payload=ExpandImageRequestPayload(image=image_url, aspect_ratio="1:1"))
        return {"result": response.get_result()}
    except Exception as e:
        return {"error": str(e)}


async def main():
    bria_client = BriaClient()

    IMAGE_URLS = [
        "https://images.freeimages.com/variants/yZ8FFPgdnhd33wgxtsjFCbWt/f4a36f6589a0e50e702740b15352bc00e4bfaf6f58bd4db850e167794d05993d",
        "https://cdn.pixabay.com/photo/2024/10/13/14/30/boy-9117346_1280.jpg",
        "https://cdn.pixabay.com/photo/2025/09/10/11/30/grief-9826220_1280.jpg",
    ]

    print(f"📷 Processing {len(IMAGE_URLS)} images concurrently...")
    print("\n🔄 Creating tasks for all images...")
    task_creation_tasks = [process_single_image(client=bria_client,image_url=url, index=i) for i, url in enumerate(IMAGE_URLS)]
    task_results = await asyncio.gather(*task_creation_tasks, return_exceptions=True)

    for result in task_results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
