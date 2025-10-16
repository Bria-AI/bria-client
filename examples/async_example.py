# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx==0.28.1", "pydantic==2.11.10", "pydantic-settings==2.11.0"]
# ///

"""
Example script demonstrating async usage of the Bria SDK.
"""

import asyncio
import os
import sys
from typing import Final

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bria_sdk import BriaSDK
from bria_sdk.engine_api.schemas.image_editing_apis.background_editing import RemoveBackgroundRequestPayload
from bria_sdk.engine_api.schemas.image_editing_apis.size_editing import ExpandImageRequestPayload
from bria_sdk.engine_api.schemas.status_api import StatusAPIResponse

# Initialize the SDK
sdk = BriaSDK()

# Example image URL
IMAGE_URL: Final[str] = "https://images.freeimages.com/variants/yZ8FFPgdnhd33wgxtsjFCbWt/f4a36f6589a0e50e702740b15352bc00e4bfaf6f58bd4db850e167794d05993d"

async def main():
    print("🚀 Running async operations...")
    print(f"📷 Image URL: {IMAGE_URL}")
    
    try:
        # Remove background
        print("\nRemoving background...")
        bg_response: StatusAPIResponse = await sdk.engine_apis.image_editing.background.remove(
            payload=RemoveBackgroundRequestPayload(image=IMAGE_URL)
        )
        print(f"✅ Background removed! Result: {bg_response.result.image_url}")
        
        # Expand image
        print("\n📐 Expanding image...")
        expand_response: StatusAPIResponse = await sdk.engine_apis.image_editing.size.expand_image(
            payload=ExpandImageRequestPayload(
                image=IMAGE_URL,
                aspect_ratio="1:1"
            )
        )
        print(f"✅ Image expanded! Result: {expand_response.result.image_url}")
    except AttributeError as e:
        print(f"❌ Result error: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
