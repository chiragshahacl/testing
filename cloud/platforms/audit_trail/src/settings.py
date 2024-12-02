from common_schemas import Base64String
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Environment
    DEBUG: bool = False
    LOG_LEVEL: str = "ERROR"
    GUNICORN_WORKERS: int = 3
    ENVIRONMENT: str
    APPLICATION_PORT: int = 80
    BASE_PATH: str
    SIBEL_VERSION: str

    # Sentry
    SENTRY_DSN: str
    SENTRY_TRACE_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    # Database
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    MAX_REGISTRY_IN_DB: int

    # Kafka
    KAFKA_HOST: str
    KAFKA_PORT: str
    KAFKA_PASSWORD: str
    KAFKA_CA_FILE_PATH: str
    KAFKA_CERT_FILE_PATH: str
    KAFKA_KEY_FILE_PATH: str
    KAFKA_RETRY_BACKOFF: int = 2000
    KAFKA_METADATA_MAX_AGE: int = 300000

    # Kafka publisher topics
    DEVICE_EVENTS_TOPIC: str
    PATIENT_EVENTS_TOPIC: str
    AUTH_EVENTS_TOPIC: str

    # Kafka consumer group id
    CONSUMER_AUDIT_TRAIL_GROUP_ID: str = "audit-trail-consumer"

    # Auth
    JWT_VERIFYING_KEY: Base64String

    # Healthcheck
    KAFKA_HEALTHCHECK_TOPIC: str


settings = Settings()
