from bria_client.results import BriaResult


class StructuredPromptResult(BriaResult):
    seed: int
    structured_prompt: dict


class StructuredPromptLiteResult(StructuredPromptResult): ...
