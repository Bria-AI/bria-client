from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from bria_engine_api.constants import BRIA_ENGINE_PRODUCTION_URL


class BriaEngineSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BRIA_ENGINE_", extra="ignore")

    URL: HttpUrl = BRIA_ENGINE_PRODUCTION_URL
    API_KEY: str | None = None


engine_settings = BriaEngineSettings()
