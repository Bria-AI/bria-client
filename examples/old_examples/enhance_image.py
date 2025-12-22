# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx==0.28.1", "httpx-retries==0.4.5", "pydantic==2.11.10", "pydantic-settings==2.11.0", "strenum==0.4.15"]
# ///

"""
Example script demonstrating image enhancement using the Bria SDK.
"""

import os
import sys
from typing import Final

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bria_client.payloads.image_editing.size_editing import EnhanceImageRequestPayload, Resolution
from bria_client.payloads.status_api import StatusAPIResponse

from bria_client import BriaClient

# Initialize the SDK
bria_client = BriaClient()

# Example image URL
IMAGE_URL: Final[str] = "https://images.freeimages.com/variants/yZ8FFPgdnhd33wgxtsjFCbWt/f4a36f6589a0e50e702740b15352bc00e4bfaf6f58bd4db850e167794d05993d"

print("✨ Enhancing image quality...")
print(f"📷 Image URL: {IMAGE_URL}")

try:
    response: StatusAPIResponse = bria_client.image_editing.enhance_image(
        payload=EnhanceImageRequestPayload(image=IMAGE_URL, resolution=Resolution.FOUR_MEGA_PIXEL)
    )

    print("✅ Image enhancement completed!")
    print(f"🔗 Result URL: {response.get_result().image_url}")

except Exception as e:
    print(f"❌ Error: {e}")
