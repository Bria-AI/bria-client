from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.structured_prompt.api import StructuredPromptAPI
from bria_client.payloads.structured_prompt_generation_payload import StructuredPromptLitePayload, StructuredPromptPayload
from bria_client.results.structured_prompt_generation import StructuredPromptLiteResult, StructuredPromptResult


class StructuredPromptGenerationAPI(StructuredPromptAPI):
    """
    currently runs FIBO
    """

    path = "generate"

    @api_endpoint("")
    def structured_prompt_generation(self, payload: StructuredPromptPayload):
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=StructuredPromptResult)
        return response

    @api_endpoint("lite")
    def structured_prompt_generation_lite(self, payload: StructuredPromptLitePayload):
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=StructuredPromptLiteResult)
        return response
