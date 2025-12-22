import logging

from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.image.image_api import ImageAPI
from bria_client.responses.image_editing_responses import (
    BlurBackgroundResponse,
    CropForegroundResponse,
    EnhanceImageResponse,
    EraseForegroundResponse,
    EraserResponse,
    ExpandImageResponse,
    GenFillResponse,
    IncreaseResResponse,
    RemoveBackgroundResponse,
)
from bria_client.schemas.image_editing_apis import (
    BlurBackgroundInput,
    CropForegroundRequestPayload,
    EnhanceImageRequestPayload,
    EraseForegroundRequestPayload,
    ExpandImageRequestPayload,
    IncreaseResolutionRequestPayload,
    ObjectEraserRequestPayload,
    ObjectGenFillRequestPayload,
    RemoveBackgroundRequestPayload,
    ReplaceBackgroundRequestPayload,
)


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

    @api_endpoint("crop_foreground")
    def crop_foreground(self, payload: CropForegroundRequestPayload):
        """
        Crop the foreground of an image

        Args:
            `payload: CropForegroundRequestPayload` - The payload for the crop foreground request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response = self.api_engine.post(url=self.url, payload=payload, response_obj=CropForegroundResponse)
        return response

    @api_endpoint("erase_foreground")
    def erase_foreground(self, payload: EraseForegroundRequestPayload):
        """
        Erase the foreground of an image

        Args:
            `payload: EraseForegroundRequestPayload` - The payload for the erase foreground request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response = self.api_engine.post(url=self.url, payload=payload, response_obj=EraseForegroundResponse)
        return response

    @api_endpoint("expand")
    def expand_image(self, payload: ExpandImageRequestPayload):
        """
        Expand the provided image to a new size by aspect ratio or by pixel sizes

        Args:
            `payload: ExpandImageRequestPayload` - The payload for the expand image request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response` - StatusAPIResponse if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response = self.api_engine.post(url=self.url, payload=payload, response_obj=ExpandImageResponse)
        return response

    @api_endpoint("enhance")
    def enhance_image(self, payload: EnhanceImageRequestPayload):
        """
        Enhance the provided image by improving the quality and resolution

        Args:
            `payload: EnhanceImageRequestPayload` - The payload for the enhance image request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - StatusAPIResponse if wait_for_status is True, else httpx.Response

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response = self.api_engine.post(url=self.url, payload=payload, response_obj=EnhanceImageResponse)
        return response

    @api_endpoint("increase_resolution")
    def increase_resolution(self, payload: IncreaseResolutionRequestPayload):
        """
        Increase the resolution of the provided image

        Args:
            `payload: IncreaseResolutionRequestPayload` - The payload for the increase resolution request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API
            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable
            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response = self.api_engine.post(url=self.url, payload=payload, response_obj=IncreaseResResponse)
        return response

    @api_endpoint("erase")
    def erase(self, payload: ObjectEraserRequestPayload):
        """
        Erase an object from an image using a mask

        Args:
            `payload: ObjectEraserRequestPayload` - The payload for the object eraser request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response = self.api_engine.post(url=self.url, payload=payload, response_obj=EraserResponse)
        return response

    @api_endpoint("gen_fill")
    def gen_fill(self, payload: ObjectGenFillRequestPayload):
        """
        Generate a fill for the provided image using a mask and a prompt to fill the masked area

        Args:
            `payload: ObjectGenFillRequestPayload` - The payload for the object gen fill request
            `wait_for_status: bool = True` - Whether to wait for the status request (locally)

        Returns:
            `Response | StatusAPIResponse` - `StatusAPIResponse` if `wait_for_status` is True, else `httpx.Response`

        Raises:
            `EngineAPIException` - In cases error is returned from the API

            `ContentModerationException` - In cases content moderation is enabled and the image is not suitable

            `TimeoutError` - If the timeout is reached while waiting for the status request
        """
        response = self.api_engine.post(url=self.url, payload=payload, response_obj=GenFillResponse)
        return response


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger("bria_client").setLevel(logging.DEBUG)

    from bria_client import BriaClient
    from bria_client.schemas.image_editing_apis import BlurBackgroundInput

    client = BriaClient(base_url="https://engine.prod.bria-api.com", api_token="a10d6386dd6a11ebba800242ac130004")
    response = client.image_editing.replace_background(
        payload=ReplaceBackgroundRequestPayload(sync=True, image="https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png")
    )
    actual = response.wait_for_status(client)
    x = 1
