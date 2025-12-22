import logging

from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.image.image_api import ImageAPI
from bria_client.responses.image_editing_responses import BlurBackgroundResponse, RemoveBackgroundResponse
from bria_client.schemas.image_editing_apis import BlurBackgroundInput, RemoveBackgroundRequestPayload, ReplaceBackgroundRequestPayload


class ImageEditingAPI(ImageAPI):
    path = "edit"

    @api_endpoint("blur_background")
    def blur_background(self, payload: BlurBackgroundInput):
        """
        Blur the background of the image

        Args:
           `payload: BlurBackgroundRequestPayload` - The payload for the blur background request
           `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
           `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
           `EngineAPIException` - In cases error is returned from the API

           `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

           `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response = self.api_engine.post(url=self.url, payload=payload, response_obj=BlurBackgroundResponse)
        return response

    @api_endpoint("remove_background")
    def remove_background(self, payload: RemoveBackgroundRequestPayload):
        """
        Remove background from image

        Args:
            `payload: RemoveBackgroundRequestPayload` - The payload for the background remove request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response = self.api_engine.post(url=self.url, payload=payload, response_obj=RemoveBackgroundResponse)
        return response

    @api_endpoint("replace_background")
    def replace_background(self, payload: ReplaceBackgroundRequestPayload):
        """
        Replace the background of the image

        Args:
            `payload: ReplaceBackgroundRequestPayload` - The payload for the replace background request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response = self.api_engine.post(url=self.url, payload=payload, response_obj=RemoveBackgroundResponse)
        return response


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger("bria_client").setLevel(logging.DEBUG)

    from bria_client import BriaClient
    from bria_client.schemas.image_editing_apis import BlurBackgroundInput

    client = BriaClient(base_url="https://engine.prod.bria-api.com", api_token="a10d6386dd6a11ebba800242ac130004")
    response = client.also_image_editing.replace_background(
        payload=ReplaceBackgroundRequestPayload(sync=True, image="https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png")
    )
    actual = response.wait_for_status(client)
    x = 1
