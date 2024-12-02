from common_schemas import Base64String, CsvString
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Environment
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    GUNICORN_WORKERS: int = 1
    ENVIRONMENT: str
    APPLICATION_PORT: int = 80
    BASE_PATH: str
    SIBEL_VERSION: str
    WEB_BASE_URL: str
    CORS_ORIGINS: CsvString

    # Sentry
    SENTRY_DSN: SecretStr
    SENTRY_TRACE_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    # Broker - General
    BROKER_TOPIC_VITALS: str
    BROKER_TOPIC_ALERTS: str
    BROKER_TOPIC_PATIENTS: str
    BROKER_TOPIC_DEVICES: str
    BROKER_TOPIC_SDC_REALTIME_STATE: str
    BROKER_TOPIC_SDC_EVENTS: str

    # Broker - Kafka
    KAFKA_HOST: str
    KAFKA_PORT: str
    KAFKA_PASSWORD: SecretStr
    KAFKA_CA_FILE_PATH: str
    KAFKA_CERT_FILE_PATH: str
    KAFKA_KEY_FILE_PATH: str
    KAFKA_RETRY_BACKOFF: int = 1000
    KAFKA_METADATA_MAX_AGE: int = 300000

    # Auth
    JWT_VERIFYING_KEY: Base64String

    # Healthcheck
    KAFKA_HEALTHCHECK_TOPIC: str


config = Settings()
