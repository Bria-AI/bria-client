from bria_client.schemas.image_editing_apis import ContentModeratedPayloadModel


class EraseForegroundRequestPayload(ContentModeratedPayloadModel):
    image: str
    preserve_alpha: bool | None = None
    sync: bool | None = None


class CropForegroundRequestPayload(ContentModeratedPayloadModel):
    image: str
    padding: int | None = None
    force_background_detection: bool | None = None
    preserve_alpha: bool | None = None
    sync: bool | None = None
