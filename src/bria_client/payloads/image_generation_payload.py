from bria_client.payloads.bria_payload import (
    ImagesInputPayload,
    IpSignalInputPayload,
    SeedInputParam,
)


class ImageGenerationPayload(ImagesInputPayload, IpSignalInputPayload, SeedInputParam):
    model_version: str | None = None
    aspect_ratio: str | None = None


class ImageGenerationLitePayload(ImageGenerationPayload): ...
