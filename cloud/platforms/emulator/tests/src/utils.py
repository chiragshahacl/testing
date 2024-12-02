import asyncio
import uuid
from collections import defaultdict
from datetime import datetime
from queue import Queue
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID

import orjson

from settings import settings
from src.common.schemas import BrokerMessage
from src.emulator.virtual_devices import (
    VIRTUAL_DEVICE_CLASS_BY_CODE,
    RunningEmulator,
    VirtualDevice,
)


class AnyUUID:
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, UUID):
            return True
        elif isinstance(other, str):
            try:
                UUID(other)
                return True
            except ValueError:
                return False
        return False


class EncryptedString:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if self.value is None:
            return other is None

        return self.value == other


class MockPublisher:
    def __init__(self):
        self._queue = Queue()

    def add_message(self, message: BrokerMessage) -> None:
        self._queue.put_nowait(message)

    async def send_and_wait(
        self,
        topic: str,
        value: bytes,
        key: bytes,
        headers: list[tuple[str, bytes], ...],
    ) -> None:
        if self._queue.empty():
            raise RuntimeError("Message not found")

        expected_message = self._queue.get_nowait()

        assert expected_message.get("topic") == topic, "Topic does not match."
        assert expected_message.get("key") == key.decode(), "Keys does not match."
        assert expected_message.get("headers") == headers

        decoded_message = orjson.loads(value)
        assert decoded_message.get("message_id") == AnyUUID()
        assert isinstance(
            datetime.strptime(decoded_message.get("timestamp"), settings.TIMESTAMP_FORMAT),
            datetime,
        )

        payload = decoded_message.get("payload")
        patient = payload.pop("patient", None)
        expected_payload = expected_message.get("value").get("payload")
        expected_patient = expected_payload.pop("patient", None)

        if expected_patient:
            for key in ["given_name", "family_name", "birth_date"]:
                assert patient[key] == EncryptedString(expected_patient[key])

        expected_determination_time = expected_payload.pop("determination_time", None)
        if expected_determination_time:
            determination_time = payload.pop("determination_time")
            assert isinstance(
                datetime.strptime(determination_time, settings.TIMESTAMP_FORMAT),
                datetime,
            )

        assert payload == expected_payload, f"""Expected message does not match:
            \nMessage:
            \n{payload}
            \nExpected message:
            \n{expected_payload}"""

    def assert_no_pending_messages(self) -> None:
        assert self._queue.empty()


class MockEmulationManager:
    _running_devices: set = set()
    _emulations: defaultdict[str, Queue[tuple]] = defaultdict(Queue)

    @classmethod
    def add_emulation(
        cls,
        expected_emulator_class,
        patient_primary_identifier,
        device_primary_identifier,
        device_code,
        modes,
    ):
        cls._emulations[device_primary_identifier].put_nowait(
            (
                expected_emulator_class,
                patient_primary_identifier,
                device_primary_identifier,
                device_code,
                modes,
            )
        )

    @classmethod
    def start_emulation(
        cls,
        patient_primary_identifier,
        device_primary_identifier,
        device_code=None,
        modes=None,
    ):
        expected_emulations = cls._emulations.get(device_primary_identifier, None)
        if not expected_emulations:
            raise RuntimeError("Emulation not found")

        if expected_emulations.empty():
            raise RuntimeError(
                f"There are no defined emulation for device {device_primary_identifier}"
            )

        if device_primary_identifier in cls._running_devices:
            raise RuntimeError(f"Emulation for device {device_primary_identifier} already running")

        expected_emulation = expected_emulations.get_nowait()
        if expected_emulations.empty():
            cls._emulations.pop(device_primary_identifier)

        cls._running_devices.add(device_primary_identifier)

        expected_emulator_class = VIRTUAL_DEVICE_CLASS_BY_CODE.get(device_code)
        virtual_device = expected_emulator_class(
            str(uuid.uuid4()),
            str(patient_primary_identifier),
            str(device_primary_identifier),
        )

        for emulator in virtual_device.emulators:
            emulator_instance = emulator(
                virtual_device.patient_primary_identifier,
                virtual_device.device_primary_identifier,
                device_type=virtual_device.type,
                mode=None,
            )
            virtual_device.running_emulators[emulator_instance.name] = RunningEmulator(
                task=AsyncMock(),
                emulator=emulator,
                current_mode=emulator_instance.mode,
            )

        assert expected_emulation[0] == expected_emulator_class
        assert expected_emulation[1] == patient_primary_identifier
        assert expected_emulation[2] == device_primary_identifier
        assert expected_emulation[3] == device_code

        if expected_emulation[4]:
            new_emulator_modes = [(key, value) for key, value in modes.items()]
            expected_modes = [(key, value) for key, value in expected_emulation[4].items()]
            assert all(mode in new_emulator_modes for mode in expected_modes)

        return AsyncMock(), virtual_device

    @classmethod
    def stop_emulation(cls, base_task: asyncio.Task, virtual_device: VirtualDevice):
        running_emulation = virtual_device.device_primary_identifier in cls._running_devices
        if not running_emulation:
            raise RuntimeError("Emulation never started")
        cls._running_devices.remove(virtual_device.device_primary_identifier)

    @classmethod
    def assert_no_pending_emulations(cls) -> None:
        assert len(cls._emulations) == 0
