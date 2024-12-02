import json

from loguru import logger

from src.streams import BrokerMessage


class MetricsCacheService:
    _instance = None
    _patient_metrics: dict[str, dict[str, dict[str, str]]] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MetricsCacheService, cls).__new__(cls)
        return cls._instance

    def _store(self, patient_identifier: str, code: str, device_id: str, data: str) -> None:
        self._patient_metrics.setdefault(patient_identifier, {}).setdefault(device_id, {})[code] = (
            data
        )

    def _remove_all(self, patient_identifier: str, device_id: str):
        self._patient_metrics.setdefault(patient_identifier, {}).pop(device_id, None)

    async def new_metrics_handler(self, message: BrokerMessage) -> None:
        if message.headers.code and message.headers.device_primary_identifier:
            self._store(
                message.key,
                message.headers.code,
                message.headers.device_primary_identifier,
                message.value,
            )

    async def sensor_removed_handler(self, message: BrokerMessage) -> None:
        parsed_message = json.loads(message.value)
        message_payload = parsed_message.get("payload", {})
        patient_identifier = message_payload.get("patient_primary_identifier")
        device_id = message_payload.get("device_primary_identifier")
        logger.info(
            f"Clearing cached metrics for patient '{patient_identifier}' and device '{device_id}'"
        )
        self._remove_all(patient_identifier, device_id)

    def get_cached_metrics(self, patient_identifier: str) -> list[str]:
        metrics = []
        for metrics_by_code in self._patient_metrics.get(patient_identifier, {}).values():
            metrics += metrics_by_code.values()
        return metrics

    def reset(self):
        self._patient_metrics = {}
