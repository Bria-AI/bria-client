from bria_client.schemas.base_models import APIPayloadModel


class VideoGenerationByTailoredImageRequestPayload(APIPayloadModel):
    model_id: str
    image: str
    seed: int | None = None
