from bria_client.engines.base.api_engine import ApiEngine


class InternalRequestEngine(ApiEngine):
    @property
    def headers(self):
        headers = super().headers.copy()
        headers.update({"X-Internal-Request": "true"})
        return headers
