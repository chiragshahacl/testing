import asyncio
import uuid

from src.emulator.virtual_devices import VIRTUAL_DEVICE_CLASS_BY_CODE, VirtualDevice


class TaskManager:
    @classmethod
    def start_emulation(
        cls,
        patient_primary_identifier,
        device_primary_identifier,
        device_code=None,
        modes=None,
    ) -> tuple[asyncio.Task, VirtualDevice]:
        VirtualDeviceClass = VIRTUAL_DEVICE_CLASS_BY_CODE.get(  # pylint: disable=C0103
            device_code
        )
        virtual_device = VirtualDeviceClass(  # pylint: disable=C0103
            str(uuid.uuid4()),
            str(patient_primary_identifier) if patient_primary_identifier else None,
            str(device_primary_identifier),
        )

        loop = asyncio.get_running_loop()
        task = loop.create_task(virtual_device.start_emulation(modes=modes))
        return task, virtual_device

    @classmethod
    def stop_emulation(cls, base_task: asyncio.Task, virtual_device: VirtualDevice):
        virtual_device.stop_emulation()
        base_task.cancel()
