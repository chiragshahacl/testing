import abc
import asyncio
from dataclasses import dataclass
from typing import Dict, Set, Type

from src.emulator import emulators
from src.emulator.constants import (
    DeviceEmulationModes,
    DeviceEmulationNames,
    DeviceTypes,
)


@dataclass
class RunningEmulator:
    task: asyncio.Task
    emulator: Type[emulators.DeviceDataEmulator]
    current_mode: DeviceEmulationModes


class VirtualDevice(abc.ABC):
    device_id: str
    running_emulators: Dict[str, RunningEmulator]

    def __init__(
        self,
        device_id: str,
        patient_primary_identifier: str,
        device_primary_identifier: str,
    ) -> None:
        self.device_id = device_id
        self.patient_primary_identifier = patient_primary_identifier
        self.device_primary_identifier = device_primary_identifier
        self.running_emulators = {}

    @property
    @abc.abstractmethod
    def type(self) -> DeviceTypes:
        """Sensor type"""

    @property
    @abc.abstractmethod
    def emulators(self) -> Set[Type[emulators.DeviceDataEmulator]]:
        """Available sensor emulators"""

    def stop_emulation(self) -> None:
        for emulator in self.running_emulators.values():
            emulator.task.cancel()

    async def start_emulation(self, modes=None):
        tasks = []
        for emulator in self.emulators:
            mode = modes.get(emulator.name) or None if modes is not None else None
            emulator_instance = emulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                device_type=self.type,
                mode=mode,
            )
            task = asyncio.create_task(emulator_instance(mode=mode))
            tasks.append(task)
            self.running_emulators[emulator_instance.name] = RunningEmulator(
                task=task,
                emulator=emulator,
                current_mode=emulator_instance.mode,
            )
        return await asyncio.gather(*tasks)

    def get_emulation_modes(self) -> Dict[str, DeviceEmulationModes]:
        modes = {}

        for name, emulator in self.running_emulators.items():
            modes[name] = emulator.current_mode

        return modes

    def has_emulator(self, emulation_name: DeviceEmulationNames) -> bool:
        return emulation_name in {e.name for e in self.emulators}


class PatientMonitor(VirtualDevice):
    type = DeviceTypes.PATIENT_MONITOR
    emulators = {
        emulators.MonitorConnectionStatusEmulator,
    }


class AdamSensor(VirtualDevice):
    type = DeviceTypes.ADAM
    emulators = {
        emulators.HeartRateEmulator,
        emulators.ChestTemperatureEmulator,
        emulators.FallsEmulator,
        emulators.PositionEmulator,
        emulators.RespiratoryRateEmulator,
        emulators.DeviceSignalEmulator,
        emulators.DeviceBatteryEmulator,
        emulators.DeviceModuleStateEmulator,
    }


class AnneChestSensor(VirtualDevice):
    type = DeviceTypes.ANNE_CHEST
    emulators = {
        emulators.CardiacEmulator,
        emulators.ChestTemperatureEmulator,
        emulators.FallsEmulator,
        emulators.PositionEmulator,
        emulators.RespiratoryRateEmulator,
        emulators.BodyAngleEmulator,
        emulators.DeviceSignalEmulator,
        emulators.DeviceBatteryChargingStatusEmulator,
        emulators.DeviceBatteryEmulator,
        emulators.DeviceModuleStateEmulator,
        emulators.DeviceLeadStateEmulator,
    }


class AnneLimbSensor(VirtualDevice):
    type = DeviceTypes.ANNE_LIMB
    emulators = {
        emulators.PLETHEmulator,
        emulators.BloodOxygenEmulator,
        emulators.PulseRateEmulator,
        emulators.PerfusionIndexEmulator,
        emulators.LimbTemperatureEmulator,
        emulators.DeviceSignalEmulator,
        emulators.DeviceBatteryChargingStatusEmulator,
        emulators.DeviceBatteryEmulator,
        emulators.DeviceModuleStateEmulator,
        emulators.DeviceContactStateEmulator,
    }


class Nonin3150Sensor(VirtualDevice):
    type = DeviceTypes.NONIN_3150
    emulators = {
        emulators.PLETHEmulator,
        emulators.BloodOxygenEmulator,
        emulators.PulseRateEmulator,
        emulators.PerfusionIndexEmulator,
        emulators.DeviceSignalEmulator,
        emulators.DeviceBatteryChargingStatusEmulator,
    }


class ViatomBPSensor(VirtualDevice):
    type = DeviceTypes.VIATOM_BP
    emulators = {
        emulators.BloodPressureEmulator,
        emulators.PulseEmulator,
        emulators.MeanArterialPressureEmulator,
        emulators.DeviceSignalEmulator,
        emulators.DeviceModuleStateEmulator,
        emulators.DeviceLeadStateEmulator,
    }


class JoytechThermometerSensor(VirtualDevice):
    type = DeviceTypes.JOYTECH_THERMOMETER
    emulators = {
        emulators.BodyTemperatureEmulator,
        emulators.DeviceSignalEmulator,
        emulators.DeviceModuleStateEmulator,
    }


VIRTUAL_DEVICE_CLASS_BY_CODE: Dict[str, Type[VirtualDevice]] = {
    DeviceTypes.PATIENT_MONITOR.value: PatientMonitor,
    DeviceTypes.ADAM.value: AdamSensor,
    DeviceTypes.ANNE_CHEST.value: AnneChestSensor,
    DeviceTypes.ANNE_LIMB.value: AnneLimbSensor,
    DeviceTypes.VIATOM_BP.value: ViatomBPSensor,
    DeviceTypes.NONIN_3150.value: Nonin3150Sensor,
    DeviceTypes.JOYTECH_THERMOMETER.value: JoytechThermometerSensor,
}
