from bria_client.payloads.bria_payload import (
    ImagesInputPayload,
    IpSignalInputPayload,
    SeedInputParam,
)


class StructuredPromptPayload(ImagesInputPayload, IpSignalInputPayload, SeedInputParam):
    structured_prompt: str | None = None


class StructuredPromptLitePayload(StructuredPromptPayload): ...
