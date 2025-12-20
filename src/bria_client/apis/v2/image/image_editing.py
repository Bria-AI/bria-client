from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.image.image_api import ImageAPI
from bria_client.responses.image_editing_responses import BlurBackgroundResponse
from bria_client.schemas.image_editing_apis import BlurBackgroundInput


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


if __name__ == "__main__":
    # TODO: make this work
    from bria_client import BriaClient
    from bria_client.schemas.image_editing_apis import BlurBackgroundInput

    client = BriaClient(base_url="https://engine.prod.bria-api.com", api_token="a10d6386dd6a11ebba800242ac130004")
    response = client.also_image_editing.blur_background(
        payload=BlurBackgroundInput(sync=False, image="https://images.unsplash.com/photo-1749735531899-aea6fba596e0?bypass=true")
    )
    actual = response.wait_for_status(client)
    x = 1
