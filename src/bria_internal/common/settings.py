from core.env import Env, Environment
from dotenv import load_dotenv
from pydantic import HttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class BriaEngineSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BRIA_ENGINE_", extra="ignore")
    _env: Env = Env()

    URL: HttpUrl | None = None
    API_KEY: str | None = None

    @computed_field
    @property
    def ENVIRONMENT(self) -> Environment:
        return self._env.environment

    @computed_field
    @property
    def IS_PRODUCTION(self) -> bool:
        return self._env.is_production()


engine_settings = BriaEngineSettings()
