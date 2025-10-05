from enum import Enum

from pydantic import Field, HttpUrl, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    PRODUCTION = "production"
    INTEGRATION = "integration"
    DEVELOPMENT = "development"  # (previously called local)


class EnvConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BRIA_ENGINE_URL: HttpUrl | None = None
    BRIA_ENGINE_API_KEY: str | None = None

    # Watching for the ENVIRONMENT key in the .env file
    ENVIRONMENT: Environment = Field(default=Environment.PRODUCTION, alias="ENVIRONMENT")

    @computed_field
    @property
    def IS_PRODUCTION(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION.value

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def _validate_environment(cls, v: str) -> Environment:
        """
        Returns the environment enum value
        """
        return Environment(v)


env_config = EnvConfig()
