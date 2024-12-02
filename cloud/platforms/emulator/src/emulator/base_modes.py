import abc
import asyncio
import itertools
import random
import uuid
from abc import abstractmethod
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Generator, List, Optional

import more_itertools
import numpy as np
from loguru import logger

from src.broker import publish, publish_pm_connection_status
from src.emulator.constants import AlarmCodes, AlarmPriorities, DeviceTypes
from src.settings import settings


@dataclass
class Alarm:
    code: AlarmCodes
    priority: AlarmPriorities
    description: str
    active: bool
    determination_time: str
    device_code: str


class ConnectionStatusTask(abc.ABC):
    task_id: uuid.UUID
    device_primary_identifier: str
    device_type: str

    def __init__(
        self,
        patient_primary_identifier: str,  # pylint: disable=W0613
        device_primary_identifier: str,
        device_type: str,
    ) -> None:
        self.task_id = uuid.uuid4()
        self.device_primary_identifier = device_primary_identifier
        self.device_type = device_type

    @property
    @abstractmethod
    def interval(self) -> float:
        """Interval between messages"""

    @property
    @abstractmethod
    def generated_value(self) -> bool:
        """Value to be sent"""

    async def __call__(self, *args, **kwargs) -> None:
        while True:
            await publish_pm_connection_status(
                self.device_primary_identifier,
                self.generated_value,
            )
            logger.debug(
                f"Patient monitor {self.device_primary_identifier} "
                f"status sent with value {self.generated_value}"
            )
            await asyncio.sleep(float(self.interval))


class EmulationTask(abc.ABC):
    task_id: uuid.UUID
    patient_primary_identifier: str
    device_primary_identifier: str
    device_type: DeviceTypes
    alarm: Optional[Alarm]

    def __init__(
        self,
        patient_primary_identifier: str,
        device_primary_identifier: str,
        device_type: DeviceTypes,
    ) -> None:
        self.task_id = uuid.uuid4()
        self.patient_primary_identifier = patient_primary_identifier
        self.device_primary_identifier = device_primary_identifier
        self.device_type = device_type

    @property
    @abstractmethod
    def interval(self) -> float:
        """Interval between messages"""

    @abstractmethod
    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Emulated message to be sent to the broker"""

    @abstractmethod
    def get_values_generator(self) -> Generator[Any, None, None]:
        """Generator of valid values"""

    async def __call__(self, *args, **kwargs) -> None:
        values_generator = self.get_values_generator()
        while True:
            message = self.get_emulated_message(next(values_generator))
            await publish(message, self.patient_primary_identifier)
            logger.debug(message)
            await asyncio.sleep(float(self.interval))


class MetricEmulator(EmulationTask, abc.ABC):
    step_value: float = float(Decimal("1.0"))
    round_value: int = 1

    @property
    @abstractmethod
    def sample_code(self) -> str:
        """Sample code to be sent along the message"""

    @property
    @abstractmethod
    def coded_value(self) -> str:
        """Unit code value to be sent along the message"""

    @property
    @abstractmethod
    def min_value(self) -> float:
        """Minimum valid value"""

    @property
    @abstractmethod
    def max_value(self) -> float:
        """Maximum valid value"""

    def get_values_generator(self) -> Generator[float, None, None]:
        while True:
            yield from np.round(
                np.arange(self.min_value, self.max_value + self.step_value, self.step_value),
                self.round_value,
            )

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        data = {
            "message_id": str(uuid.uuid4()),
            "event_type": "NEW_METRICS",
            "event_name": "New metrics",
            "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
            "payload": {
                "patient_primary_identifier": self.patient_primary_identifier,
                "samples": [value],
                "determination_time": datetime.utcnow(),
                "unit_code": self.coded_value,
                "code": self.sample_code,
                "device_code": self.device_type.value,
                "device_primary_identifier": self.device_primary_identifier,
            },
        }
        return data


class IntegerMetricEmulator(MetricEmulator, abc.ABC):
    step_value: int = 1

    def get_values_generator(self) -> Generator[int, None, None]:
        while True:
            for i in super().get_values_generator():
                yield int(i)


class FloatMetricEmulator(MetricEmulator, abc.ABC):
    step_value: float = 1.0


class StringEnumEmulator(EmulationTask, abc.ABC):
    @property
    @abstractmethod
    def sample_code(self) -> str:
        """Sample code to be sent along the message"""

    @abstractmethod
    def get_values(self) -> List[str]:
        """Returns possible string enum values"""

    def get_values_generator(self) -> str:
        while True:
            yield np.random.choice(self.get_values())

    def get_emulated_message(self, value: str) -> Dict[str, Any]:
        code = self.sample_code
        data = {
            "message_id": str(uuid.uuid4()),
            "event_type": "NEW_METRICS",
            "event_name": "New metrics",
            "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
            "payload": {
                "patient_primary_identifier": self.patient_primary_identifier,
                "samples": [value],
                "determination_time": datetime.utcnow(),
                "code": code,
                "device_code": self.device_type.value,
                "device_primary_identifier": self.device_primary_identifier,
            },
        }
        return data


class TimerEmulator(EmulationTask, abc.ABC):
    @property
    @abstractmethod
    def sample_code(self) -> str:
        """Sample code to be sent along the message"""

    @property
    @abstractmethod
    def start_value(self) -> float:
        """Starting count value"""

    @property
    @abstractmethod
    def max_value(self) -> float:
        """Max count value"""

    def get_values_generator(self) -> Generator[float, None, None]:
        yield from itertools.cycle(np.arange(self.start_value, self.max_value, self.interval))

    def get_emulated_message(self, value: int) -> Dict[str, Any]:
        code = self.sample_code
        data = {
            "message_id": str(uuid.uuid4()),
            "event_type": "NEW_METRICS",
            "event_name": "New metrics",
            "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
            "payload": {
                "patient_primary_identifier": self.patient_primary_identifier,
                "samples": [int(value)],
                "determination_time": datetime.utcnow(),
                "code": code,
                "device_code": self.device_type.value,
                "device_primary_identifier": self.device_primary_identifier,
            },
        }
        return data


class BooleanEmulator(EmulationTask, abc.ABC):
    fixed_status: Optional[bool] = None

    @property
    @abstractmethod
    def sample_code(self) -> str:
        """Sample code to be sent along the message"""

    def get_values_generator(self) -> bool:
        while True:
            if self.fixed_status is not None:
                yield self.fixed_status
            else:
                yield bool(random.getrandbits(1))

    def get_emulated_message(self, value: bool) -> Dict[str, Any]:
        code = self.sample_code
        data = {
            "message_id": str(uuid.uuid4()),
            "event_type": "NEW_METRICS",
            "event_name": "New metrics",
            "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
            "payload": {
                "patient_primary_identifier": self.patient_primary_identifier,
                "message_id": str(uuid.uuid4()),
                "samples": [value],
                "determination_time": datetime.utcnow(),
                "code": code,
                "device_code": self.device_type.value,
                "device_primary_identifier": self.device_primary_identifier,
            },
        }
        return data


class WaveformEmulator(EmulationTask, abc.ABC):
    max_samples_strict: bool = True

    @property
    @abstractmethod
    def sample_code(self) -> str:
        """Sample code to be sent along the message"""

    @property
    @abc.abstractmethod
    def dataset(self) -> List[Any]:
        """Data to be sent as sample"""

    @property
    @abc.abstractmethod
    def max_samples(self) -> int:
        """Max samples to be included"""

    @property
    @abc.abstractmethod
    def sample_period(self) -> float:
        """Sample period to be sent alongside sample data"""

    @property
    @abc.abstractmethod
    def determination_period(self) -> float:
        """Determination period to be sent alongside sample data"""

    def get_emulated_message(self, value: List[float]) -> Dict[str, Any]:
        code = self.sample_code
        data = {
            "message_id": str(uuid.uuid4()),
            "event_type": "NEW_WAVEFORM_VITALS",
            "event_name": "New waveform vitals",
            "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
            "payload": {
                "patient_primary_identifier": self.patient_primary_identifier,
                "message_id": str(uuid.uuid4()),
                "samples": value,
                "determination_time": datetime.utcnow(),
                "code": code,
                "device_code": self.device_type.value,
                "device_primary_identifier": self.device_primary_identifier,
                "sample_period": "PT" + str(self.sample_period) + "S",
                "determination_period": "PT" + str(self.determination_period) + "S",
            },
        }
        return data

    def get_values_generator(self) -> Generator[Any, None, None]:
        while True:
            with suppress(ValueError):
                yield from more_itertools.chunked(
                    self.dataset, self.max_samples, strict=self.max_samples_strict
                )
