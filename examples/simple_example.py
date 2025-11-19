# /// script
# requires-python = ">=3.10"
# dependencies = [
# "bria_client@git+https://github.com/Bria-AI/bria-client.git",
# "dotenv"
# ]
# ///

import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from bria_client import BriaClient
from bria_client.schemas.image_editing_apis.background_editing import RemoveBackgroundRequestPayload

IMAGE_URL = "https://images.freeimages.com/variants/yZ8FFPgdnhd33wgxtsjFCbWt/f4a36f6589a0e50e702740b15352bc00e4bfaf6f58bd4db850e167794d05993d"


def main():
    assert os.environ.get("BRIA_ENGINE_API_KEY"), "set BRIA_ENGINE_API_KEY for example"

    bria_client = BriaClient()
    bg_response = bria_client.image_editing.remove_background(payload=RemoveBackgroundRequestPayload(image=IMAGE_URL))
    print(f"""
    Remove Background result image url:

    {bg_response.get_result().image_url}
    """)


if __name__ == "__main__":
    main()
