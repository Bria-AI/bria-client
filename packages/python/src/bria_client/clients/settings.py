from pydantic_settings import BaseSettings, SettingsConfigDict


class BriaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BRIA_")

    api_token: str | None = None
    base_url: str = "https://engine.prod.bria-api.com"
