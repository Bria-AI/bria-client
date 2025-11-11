from bria_client.clients.engine_client import EngineClient
from bria_client.exceptions.engine_api_exception import ContentModerationException, EngineAPIException
from bria_client.schemas.image_editing_apis import ContentModeratedPayloadModel, PromptContentModeratedPayloadModel


class BriaEngineClient(EngineClient):

    @property
    def _headers(self):
        return {}

    def get_custom_exception(self, e: EngineAPIException, payload: ContentModeratedPayloadModel) -> ContentModerationException | EngineAPIException:
        """
        Converting the Broader EngineAPIException to the more specific custom exceptions models.

        Args:
            `e: EngineAPIException` - The exception to convert
            `payload: ContentModeratedPayloadModel` - The payload that was used to make the request

        Returns:
            `ContentModerationException` - If the request is not suitable for content moderation

            `EngineAPIException` - If the request is not suitable for content moderation
        """
        if e.response.status_code == 422:
            if isinstance(payload, ContentModeratedPayloadModel) and payload.is_moderated:
                return ContentModerationException.from_engine_api_exception(e)
            if isinstance(payload, PromptContentModeratedPayloadModel) and payload.is_moderated:
                return ContentModerationException.from_engine_api_exception(e)
        return e
