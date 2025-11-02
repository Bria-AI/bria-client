# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx==0.28.1", "pydantic==2.11.10", "pydantic-settings==2.11.0"]
# ///

"""
Example script demonstrating background removal using the Bria SDK.
"""

import os
import sys
from typing import Final

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bria_client import BriaClient
from bria_client.schemas.image_editing_apis.background_editing import RemoveBackgroundRequestPayload
from bria_client.schemas.status_api import StatusAPIResponse

# Initialize the SDK
bria_client = BriaClient()

# Example image URL
IMAGE_URL: Final[str] = "https://images.freeimages.com/variants/yZ8FFPgdnhd33wgxtsjFCbWt/f4a36f6589a0e50e702740b15352bc00e4bfaf6f58bd4db850e167794d05993d"

print("🦆 Removing background from image...")
print(f"📷 Image URL: {IMAGE_URL}")

try:
    response: StatusAPIResponse = bria_client.image_editing.blur(payload=RemoveBackgroundRequestPayload(image=IMAGE_URL))

    print("✅ Background removal completed!")
    print(f"🔗 Result URL: {response.get_result().image_url}")

except AttributeError as e:
    print(f"❌ Status API Result error: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
