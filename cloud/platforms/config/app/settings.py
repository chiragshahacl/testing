from common_schemas import Base64String, SecretString
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment config
    DEBUG: bool = False
    LOGURU_LEVEL: str = "ERROR"
    GUNICORN_WORKERS: int = 3
    ENVIRONMENT: str
    APPLICATION_PORT: int = 80
    BASE_PATH: str
    PUBLISHER_BACKEND: str = "app.common.event_sourcing.publisher.KafkaPublisher"
    SIBEL_VERSION: str
    SYSTEM_USERNAME: str = "system"
    CONFIG_PUBLISHER_AUDIT_TRAIL_STREAM_NAME: str = "events-config"

    # patient vitals topic params
    PATIENT_VITALS_KAFKA_TOPIC_NAME: str = "vitals-v2"
    PATIENT_VITALS_KAFKA_TOPIC_PARTITIONS: int
    PATIENT_VITALS_KAFKA_TOPIC_REPLICATION_FACTOR: int
    PATIENT_VITALS_DEFAULT_KAFKA_TOPIC_RETENTION_MS: int

    # Sentry config
    SENTRY_DSN: str
    SENTRY_TRACE_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    # Database config
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USERNAME: SecretString
    DB_PASSWORD: SecretString

    # Kafka config
    KAFKA_HOST: str
    KAFKA_PORT: str
    KAFKA_PASSWORD: SecretString
    KAFKA_CLIENT_ID: str = "config-ms"
    KAFKA_CA_FILE_PATH: str
    KAFKA_CERT_FILE_PATH: str
    KAFKA_KEY_FILE_PATH: str
    KAFKA_RETRY_BACKOFF: int = 2000
    KAFKA_METADATA_MAX_AGE: int = 300000

    # Redis config
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: SecretString
    REDIS_PASSWORD: SecretString
    REDIS_CACHE_TTL: int
    CACHE_ENABLED: bool = True
    PROJECT_NAME: str = "config"

    # Auth
    JWT_VERIFYING_KEY: Base64String

    # Healthcheck
    KAFKA_HEALTHCHECK_TOPIC: str


config = Settings()
