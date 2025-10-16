# /// script
# requires-python = ">=3.10"
# ///

"""
Example script demonstrating background removal using the Bria SDK.
"""

import os
import sys
from typing import Final

from bria_sdk.engine_api.schemas.status_api import StatusAPIResponse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bria_sdk import BriaSDK
from bria_sdk.engine_api.schemas.image_editing_apis.background_editing import RemoveBackgroundRequestPayload

# Initialize the SDK
sdk = BriaSDK()

# Example image URL
IMAGE_URL: Final[str] = "https://images.freeimages.com/variants/yZ8FFPgdnhd33wgxtsjFCbWt/f4a36f6589a0e50e702740b15352bc00e4bfaf6f58bd4db850e167794d05993d"

print("🦆 Removing background from image...")
print(f"📷 Image URL: {IMAGE_URL}")

try:
    response: StatusAPIResponse = sdk.engine_apis.image_editing.background.blur(
        payload=RemoveBackgroundRequestPayload(
            image=IMAGE_URL
        )
    )
    
    print("✅ Background removal completed!")
    print(f"🔗 Result URL: {response.result.image_url}")

except AttributeError as e:
    print(f"❌ Status API Result error: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
