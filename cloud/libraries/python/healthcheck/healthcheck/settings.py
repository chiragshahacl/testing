from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    ENVIRONMENT: str

    # Healthcheck
    KAFKA_HEALTHCHECK_PERIOD_SECONDS: int = 5
    KAFKA_HEALTHCHECK_TOLERANCE_SECONDS: int = 15
    KAFKA_HEALTHCHECK_MAXIMUM_TOLERANCE_MINUTES: int = 10
    KAFKA_HEALTHCHECK_TOPIC: str

    # Kafka
    KAFKA_HOST: str
    KAFKA_PORT: str
    KAFKA_PASSWORD: SecretStr
    KAFKA_CA_FILE_PATH: str
    KAFKA_CERT_FILE_PATH: str
    KAFKA_KEY_FILE_PATH: str
    KAFKA_RETRY_BACKOFF: int = 2000
    KAFKA_METADATA_MAX_AGE: int = 300000

    @model_validator(mode="after")
    @classmethod
    def validate_healthcheck_settings(cls, values):
        assert (
            values.KAFKA_HEALTHCHECK_TOLERANCE_SECONDS
            >= values.KAFKA_HEALTHCHECK_PERIOD_SECONDS
        ), (
            "KAFKA_HEALTHCHECK_TOLERANCE_SECONDS has to be "
            ">= KAFKA_HEALTHCHECK_PERIOD_SECONDS"
        )

        return values


settings = Settings()
