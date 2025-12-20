from httpx_retries import Retry

from bria_client.engines.base.api_engine import ApiEngine
from bria_client.exceptions.old.engine_api_exception import ContentModerationException, EngineAPIException
from bria_client.schemas.image_editing_apis import ContentModeratedPayloadModel, PromptContentModeratedPayloadModel


class BriaEngine(ApiEngine):
    def __init__(self, base_url: str, retry: Retry | None = None):
        super().__init__(base_url=base_url, retry=retry)

    def custom_exception_handle(self, e: EngineAPIException, payload: ContentModeratedPayloadModel) -> ContentModerationException | EngineAPIException:
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
