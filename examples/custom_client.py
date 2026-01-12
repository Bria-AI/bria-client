import logging
import os
from _contextvars import ContextVar

from dotenv import load_dotenv

load_dotenv()

from bria_client import BriaSyncClient
from bria_client.engines.api_engine import ApiEngine

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)

api_token_var = ContextVar("api_token", default=os.environ.get("BRIA_API_TOKEN"))


class MyCustomEngine(ApiEngine):
    def __init__(self, base_url: str | None, default_api_token: str | None = None):
        self.default_api_token = default_api_token
        super().__init__(base_url=base_url)

    @property
    def auth_headers(self) -> dict[str, str]:
        api_token = api_token_var.get() or self.default_api_token
        return {"api_token": api_token}


client = BriaSyncClient(api_engine=MyCustomEngine(base_url="https://engine.prod.bria-api.com"))

resp = client.run(endpoint="image/edit/remove_background", payload={"image": "https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png"})

print(resp)
