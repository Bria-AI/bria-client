from bria_client.apis.api import api_endpoint
from bria_client.apis.v1.v1_api import V1API
from bria_client.payloads.image_editing import GetMasksRequestPayload


class ObjectsAPI(V1API):
    path = "objects"

    @api_endpoint("mask_generator")
    async def get_masks(self, payload: GetMasksRequestPayload):
        """
        Get all the masks for an image in a package

        Args:
            `payload: GetMasksRequestPayload` - The payload for the get masks request

        Returns:
            `Response` - Response with the masks `.zip` file

        Raises:
            `HTTPStatusError` - In cases error is returned from the API

            `PollingException` - If the file polling fails
        """
        raise NotImplementedError("idk not implemented yet")
        response = self.api_engine.post(url=self.url, payload=payload, result_obj={})
        return response
