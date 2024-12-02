from decimal import Decimal
from pathlib import Path

from pydantic import BaseSettings


class CommaSeparatedStrings(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.split_on_comma

    @classmethod
    def split_on_comma(cls, value: str | None):
        if not value:
            return None

        if not isinstance(value, str):
            raise TypeError("String required")

        return [item.strip() for item in value.split(",")]


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    # Environment
    DEBUG: bool = False
    LOG_LEVEL: str = "ERROR"
    GUNICORN_WORKERS: int = 3
    ENVIRONMENT: str
    APPLICATION_PORT: int = 80
    BASE_PATH: str
    WATCHDOG_TIMEDELTA_SECONDS: float = 10
    BASE_DIR: Path = Path(__file__).resolve(strict=True).parent.parent
    CORS_ORIGINS: CommaSeparatedStrings

    # Emulator
    # Max number of patient monitors connected
    TOTAL_MONITORS: int = 64
    # Max number of sensors connected per patient monitor
    TOTAL_SENSORS_PER_MONITOR: int = 4
    # Datetime format for broker messages
    TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"

    PM_CONNECTION_STATUS_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("2.0")
    # BP
    # internal rate at which the monitor will send blood pressure data
    BP_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("1.0")
    # HR
    # internal rate at which the monitor will send heart rate data
    HR_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("1.0")

    # maximum ecg waveform datapoints sent by a monitor in a second (without buffering)
    ECG_MAXIMUM_DATAPOINTS_PER_SECOND: int = 256
    # interval at which the monitor will send ECG waveform data to the backend
    ECG_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("0.5")
    # internal rate at which the monitor will send pulse data
    PULSE_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("5.0")
    # internal rate at which the monitor will send PR data
    PR_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("5.0")

    # OXYGEN
    # internal rate at which the monitor will send spo2 data
    SPO2_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("5.0")

    # enables/Disables PI emulation
    PI_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("5.0")

    # Temperature
    # internal rate at which the monitor will send temperature data
    TEMPERATURE_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("1.0")

    # Position/Falls
    # internal rate at which the monitor will send falls data
    FALLS_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("30.0")

    # internal rate at which the monitor will send exact position data
    POSITION_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("30.0")

    POSITION_DURATION_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("30.0")

    # Devices Status
    # internal rate at which the device will send signal data
    DEVICE_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("60.0")

    # Alarms
    # internal at which the emulator evaluates if it should send the alarm
    ALARM_EVALUATION_INTERVAL: int = 15

    # RR/Pleth
    # maximum rr waveform datapoints sent by a monitor in a second (without buffering)
    RR_MAXIMUM_DATAPOINTS_PER_SECOND: int = 26

    # interval at which the monitor will send RR waveform data to the backend
    RR_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("0.5")

    # interval at which the monitor will send RR metric data to the backend
    RR_METRIC_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("20.0")

    # maximum pleth waveform datapoints sent by a monitor in a second (no buffering)
    PLETH_MAXIMUM_DATAPOINTS_PER_SECOND: int = 64

    # interval at which the monitor will send ECG waveform data to the backend
    PLETH_MESSAGE_INTERVAL_IN_SECONDS: Decimal = Decimal("0.5")

    # interval at which the monitor will send Angle Metric to the backend
    BODY_ANGLE_INTERVAL_IN_SECONDS: Decimal = Decimal("5")

    # interval at which the monitor will send Angle Metric to the backend
    MEAN_ARTERIAL_PRESSURE_INTERVAL_IN_SECONDS: Decimal = Decimal("5")

    # Kafka
    KAFKA_HOST: str
    KAFKA_PORT: str
    KAFKA_VITALS_TOPIC: str
    KAFKA_ALERTS_TOPIC: str
    KAFKA_TECHNICAL_ALERTS_TOPIC: str
    KAFKA_DEVICE_TOPIC: str
    KAFKA_SDC_REALTIME_STATE_TOPIC: str
    KAFKA_PASSWORD: str
    KAFKA_CA_FILE_PATH: str
    KAFKA_CERT_FILE_PATH: str
    KAFKA_KEY_FILE_PATH: str

    # Sentry
    SIBEL_VERSION: str

    # Fake data
    FAKE_DATA_SEED: int = 1234
    WEB_GATEWAY_URL: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    DEVICE_PLATFORM_URL: str

    # MLLP Server
    MLLP_SERVER_PORT: int = 2575
    MLLP_QUEUE_SIZE: int = 1024


settings = Settings()
