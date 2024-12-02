from pydantic import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    GITHUB_TOKEN: str | None = None
    GITHUB_REPOSITORY: str | None = None
    WORKFLOW_NAME = "Cloud - Deploy to DEV"


settings = Settings()
