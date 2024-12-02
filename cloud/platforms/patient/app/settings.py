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
    PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME: str = "events-patient"
    DEVICE_PUBLISHER_AUDIT_TRAIL_STREAM_NAME: str = "events-device"
    MAX_PATIENTS_PER_GROUP: int = 16
    MAX_BEDS: int = 64
    MAX_BEDS_PER_GROUP: int = 16
    SIBEL_VERSION: str
    SYSTEM_USERNAME: str = "system"

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
    DB_ENCRYPTION_KEY: SecretString

    # Kafka config
    KAFKA_HOST: str
    KAFKA_PORT: str
    KAFKA_PASSWORD: SecretString
    KAFKA_CA_FILE_PATH: str
    KAFKA_CERT_FILE_PATH: str
    KAFKA_KEY_FILE_PATH: str
    KAFKA_RETRY_BACKOFF: int = 2000
    KAFKA_METADATA_MAX_AGE: int = 300000

    # kafka topics
    EVENTS_ALERT_TOPIC: str = "alerts"
    EVENTS_SDC_TOPIC: str = "events-sdc"
    EVENTS_DEVICE_TOPIC: str = "events-device"

    # Kafka consumer group id
    CONSUMER_PATIENT_GROUP_ID: str = "patient-consumer"
    CONSUMER_DEVICE_GROUP_ID: str = "device-consumer"

    # Redis config
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: SecretString
    REDIS_PASSWORD: SecretString
    REDIS_CACHE_TTL: int
    CACHE_ENABLED: bool = True
    PROJECT_NAME: str = "patient"

    # Auth
    JWT_VERIFYING_KEY: Base64String

    # Healthcheck
    KAFKA_HEALTHCHECK_TOPIC: str


config = Settings()
