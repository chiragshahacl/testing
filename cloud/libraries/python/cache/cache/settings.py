from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    ENVIRONMENT: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: SecretStr
    REDIS_PASSWORD: SecretStr
    REDIS_CACHE_TTL: int = 86400
    CACHE_ENABLED: bool = True
    PROJECT_NAME: str


settings = Settings()
