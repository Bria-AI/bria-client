# /// script
# requires-python = ">=3.10"
# ///

import os
import sys
from typing import Final

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bria_engine_api.schemas.image_editing_apis.size_editing import ExpandImageRequestPayload
from bria_sdk import BriaSDK

sdk = BriaSDK()

IMAGE_URL: Final[str] = ""
response = sdk.engine_apis.image_editing.size.expand_image(
    payload=ExpandImageRequestPayload(
        image=IMAGE_URL,
        aspect_ratio="1:1"
    )
    # wait_for_status=False # Default is
)

print(response)