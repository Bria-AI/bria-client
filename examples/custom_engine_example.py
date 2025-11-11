# /// script
# requires-python = ">=3.10"
# dependencies = [
# "bria_client@git+https://github.com/Bria-AI/bria-client.git@19-feat-abstract-client-impl"
# ]
# ///
import os

from dotenv import load_dotenv

from bria_client import BriaBackend
from bria_client.engines import ApiEngine
from bria_client.exceptions import ContentModerationException, EngineAPIException
from bria_client.schemas.base_models import ContentModeratedPayloadModel
from bria_client.schemas.image_editing_apis import RemoveBackgroundRequestPayload

load_dotenv()


class MyCustomEngine(ApiEngine):
    def get_custom_exception(self, e: EngineAPIException, payload: ContentModeratedPayloadModel) -> ContentModerationException | EngineAPIException:
        print(f"Encountered exception: {str(e.__class__.__name__)}, raising my custom exception instead")
        raise Exception("This is my custom exception")


def main():
    assert os.environ.get("BRIA_ENGINE_API_KEY"), "set BRIA_ENGINE_API_KEY for example"
    client = BriaBackend(engine=MyCustomEngine())

    image = "https://invalid_url"
    response = client.image_editing.remove_background(RemoveBackgroundRequestPayload(image=image, sync=True))
    print(response)


if __name__ == "__main__":
    main()
