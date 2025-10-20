# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx==0.28.1", "pydantic==2.11.10", "pydantic-settings==2.11.0"]
# ///

"""
Example script demonstrating batch async processing of multiple images using asyncio tasks.
This example shows how to process multiple images concurrently for better performance.
"""

import asyncio
import os
import sys
from typing import Final

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bria_sdk import BriaSDK
from bria_sdk.engine_api.schemas.image_editing_apis.size_editing import ExpandImageRequestPayload
from bria_sdk.engine_api.schemas.status_api import StatusAPIResponse

# Initialize the SDK
sdk = BriaSDK()

# Example image URLs - replace with your actual image URLs
IMAGE_URLS: Final[list[str]] = [
    # Add your image URLs here
    "https://images.freeimages.com/variants/yZ8FFPgdnhd33wgxtsjFCbWt/f4a36f6589a0e50e702740b15352bc00e4bfaf6f58bd4db850e167794d05993d",
    "https://cdn.pixabay.com/photo/2024/10/13/14/30/boy-9117346_1280.jpg",
    "https://cdn.pixabay.com/photo/2025/09/10/11/30/grief-9826220_1280.jpg",
]


async def process_single_image(image_url: str, index: int) -> dict:
    try:
        print(f"🔄 Processing image {index + 1}: {image_url}")

        # Expand image with wait_for_status=False to get immediate response with `request_id` and handle the status API checking manually
        response: StatusAPIResponse = await sdk.engine_apis.image_editing.size.expand_image(
            payload=ExpandImageRequestPayload(image=image_url, aspect_ratio="1:1")
        )

        # Get the task ID from the response
        print(f"📋 Task {index + 1} created")
        return {
            "index": index,
            "original_url": image_url,
            "result": response.result or response.error,
        }

    except Exception as e:
        print(f"❌ Error processing image {index + 1}: {e}")
        return {
            "index": index,
            "original_url": image_url,
            "error": str(e),
        }


async def main():
    print("🚀 Starting batch async image processing...")

    if not IMAGE_URLS:
        print("⚠️  No image URLs provided. Please add image URLs to the IMAGE_URLS list.")
        return

    print(f"📷 Processing {len(IMAGE_URLS)} images concurrently...")
    print("\n🔄 Creating tasks for all images...")
    task_creation_tasks = [process_single_image(url, i) for i, url in enumerate(IMAGE_URLS)]

    print(task_creation_tasks)
    # Wait for all tasks to be created
    task_results = await asyncio.gather(*task_creation_tasks, return_exceptions=True)

    # Filter out failed tasks and get successful ones
    successful_tasks = [result for result in task_results if isinstance(result, dict) and "task_id" in result]
    failed_tasks = [result for result in task_results if isinstance(result, dict) and "error" in result]

    print(f"✅ Resolved {len(successful_tasks)} tasks successfully")
    if failed_tasks:
        print(f"❌ {len(failed_tasks)} tasks failed to create")

    if not successful_tasks:
        print("❌ No tasks were created successfully. Exiting.")
        return
    else:
        for successful_task in successful_tasks:
            print(f"🔗 Result URL: {successful_task}")


if __name__ == "__main__":
    asyncio.run(main())
