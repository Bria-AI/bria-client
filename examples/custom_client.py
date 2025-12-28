import logging
import os
from collections.abc import Callable
from contextvars import ContextVar

from dotenv import load_dotenv
from httpx_retries import Retry

from bria_client import BriaBackend
from bria_client.engines import ApiEngine

load_dotenv()


class MyCustomEngine(ApiEngine):
    def __init__(self, base_url: str, custom_auth_callable: Callable[[], dict], retry: Retry | None = None):
        super().__init__(base_url=base_url, default_headers=custom_auth_callable, retry=retry)


class MyCustomClient(BriaBackend):
    @property
    def _engine(self) -> ApiEngine:
        return MyCustomEngine(base_url="http://bria", custom_auth_callable=lambda: {"jwt": "token"}, retry=Retry())


from bria_client.payloads.image_editing_payload import ReplaceBgPayload

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)

api_token_var = ContextVar("api_token", default=os.environ.get("BRIA_API_TOKEN"))

client = MyCustomClient()
replace_bg_input = ReplaceBgPayload(sync=True, image="https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png", prompt="starry night")

response = client.image_editing.replace_background(payload=replace_bg_input)

print(response.result.image_url)


# if __name__ == '__main__':
#     class BriaPlatformEngine(ApiEngine):
#         def __init__(self, base_url: str, jwt_token: str, api_token: str, retry: Retry | None = None):
#             super().__init__(base_url=base_url, default_headers={"jwt_token": jwt_token, "api_token": api_token}, retry=retry)
#
#
#     class ContextVarAuthEngine(ApiEngine):
#         def __init__(self, base_url: str, api_token_ctx: ContextVar[str], retry: Retry | None = None):
#             super().__init__(base_url=base_url, default_headers=lambda: {"api_token": api_token_ctx.get()}, retry=retry)
#
#
#     class InternalRequestEngine(ApiEngine):
#         def __init__(self, base_url: str, api_token_ctx: ContextVar[str], retry: Retry | None = None):
#             super().__init__(base_url=base_url, default_headers=lambda: {"api_token": api_token_ctx.get(), "X-Internal-Request": "true"}, retry=retry)
