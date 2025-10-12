from bria_internal.schemas.image_editing_apis import ContentModeratedPayloadModel


class ReplaceForegroundRequestPayload(ContentModeratedPayloadModel):
    image: str
    preserve_alpha: bool | None = None
    sync: bool | None = None


class CropOutRequestPayload(ContentModeratedPayloadModel):
    image: str
    padding: int | None = None
    force_background_detection: bool | None = None
    preserve_alpha: bool | None = None
    sync: bool | None = None
