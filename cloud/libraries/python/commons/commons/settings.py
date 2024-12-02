from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    # Environment
    ENVIRONMENT: str


settings = Settings()
