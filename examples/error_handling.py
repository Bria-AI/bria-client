# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx==0.28.1", "pydantic==2.11.10", "pydantic-settings==2.11.0"]
# ///

"""
Example script demonstrating error handling with the Bria SDK.
"""

import os
import sys
from typing import Final

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bria_engine_api.exceptions.engine_api_exception import ContentModerationException, EngineAPIException
from bria_engine_api.schemas.image_editing_apis.background_editing import RemoveBackgroundRequestPayload
from bria_engine_api.schemas.status_api import StatusAPIResponse
from bria_sdk import BriaSDK

# Initialize the SDK
sdk = BriaSDK()

# Example image URL (using an invalid URL to demonstrate error handling)
INVALID_IMAGE_URL: Final[str] = ""

print("🔧 Demonstrating error handling...")
print(f"📷 Image URL: {INVALID_IMAGE_URL}")

try:
    response: StatusAPIResponse = sdk.engine_apis.image_editing.background.remove(
        payload=RemoveBackgroundRequestPayload(
            image=INVALID_IMAGE_URL
        )
    )
    
    print("✅ Background removal completed!")
    print(f"🔗 Result URL: {response.result.image_url}")
    
except ContentModerationException as e:
    print(f"🚫 Content moderation error: {e}")
    print("💡 The image content was flagged by moderation filters")
    
except EngineAPIException as e:
    print(f"🔌 API error: {e}")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
