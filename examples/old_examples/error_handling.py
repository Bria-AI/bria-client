# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx==0.28.1", "httpx-retries==0.4.5", "pydantic==2.11.10", "pydantic-settings==2.11.0", "strenum==0.4.15"]
# ///

"""
Example script demonstrating error handling with the Bria SDK.
"""

import os
import sys
from typing import Final

from httpx_retries import Retry

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bria_client.payloads.image_editing.background_editing import RemoveBackgroundRequestPayload
from bria_client.payloads.status_api import StatusAPIResponse

from bria_client import BriaClient
from bria_client.exceptions import ContentModerationException, EngineAPIException, UnknownStatusException

# Initialize the SDK with retry configuration for handling transient errors
retry = Retry(total=3, backoff_factor=1.0, status_forcelist=[500, 502, 503, 504])
bria_client = BriaClient(retry=retry)

# Example image URL (using an invalid URL to demonstrate error handling)
INVALID_IMAGE_URL: Final[str] = ""

print("🔧 Demonstrating error handling...")
print(f"📷 Image URL: {INVALID_IMAGE_URL}")

try:
    response: StatusAPIResponse = bria_client.image_editing.remove_background(payload=RemoveBackgroundRequestPayload(image=INVALID_IMAGE_URL))

    print("✅ Background removal completed!")
    print(f"🔗 Result URL: {response.get_result().image_url}")


except UnknownStatusException as e:
    print(f"🚫 Unknown status error: {e}")
    print("💡 The status is unknown")

except ContentModerationException as e:
    print(f"🚫 Content moderation error: {e}")
    print("💡 The image content was flagged by moderation filters")

except EngineAPIException as e:
    print(f"🔌 API error: {e}")

except Exception as e:
    print(f"❌ Unexpected error: {e}")
