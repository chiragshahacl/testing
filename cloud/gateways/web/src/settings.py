from common_schemas import Base64String, CsvString
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    DEBUG: bool = False
    LOG_LEVEL: str = "ERROR"
    GUNICORN_WORKERS: int = 3
    ENVIRONMENT: str
    APPLICATION_PORT: int = 80
    BASE_PATH: str
    PUBLISHER_BACKEND: str = "src.event_sourcing.publisher.KafkaPublisher"
    PUBLISHER_DEVICE_COMMAND_STREAM_NAME: str
    CORS_ORIGINS: CsvString
    SIBEL_VERSION: str

    # Base URLs
    PATIENT_PLATFORM_BASE_URL: str
    AUDIT_PLATFORM_BASE_URL: str
    AUTH_PLATFORM_BASE_URL: str
    DEVICE_PLATFORM_BASE_URL: str
    EHR_PLATFORM_BASE_URL: str

    # Sentry
    SENTRY_DSN: str
    SENTRY_TRACE_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    # Topics
    PM_STATE_TOPIC: str = "sdc-realtime-state"
    DEVICE_COMMAND_RESPONSE_TOPIC: str = "device-commands-responses"

    # Kafka
    KAFKA_HOST: str
    KAFKA_PORT: str
    KAFKA_PASSWORD: SecretStr
    KAFKA_CA_FILE_PATH: SecretStr
    KAFKA_CERT_FILE_PATH: SecretStr
    KAFKA_KEY_FILE_PATH: SecretStr
    KAFKA_RETRY_BACKOFF: int = 2000
    KAFKA_METADATA_MAX_AGE: int = 300000

    # Redis config
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: str
    REDIS_PASSWORD: str
    REDIS_CACHE_TTL: int = 86400
    PROJECT_NAME: str
    REDIS_SHARED_CACHE_PREFIX: str = "shared/monitoring/patient"

    # Auth
    DEFAULT_ADMIN_USERNAME: str
    DEFAULT_TECHNICAL_USER_USERNAME: str
    JWT_VERIFYING_KEY: Base64String

    # Healthcheck
    KAFKA_HEALTHCHECK_TOPIC: str


settings = Settings()
