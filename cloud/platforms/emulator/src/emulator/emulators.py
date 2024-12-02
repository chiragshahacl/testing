import abc
import uuid
from typing import Dict, Optional, Type

from src.emulator import modes as emulation_modes
from src.emulator.base_modes import (
    EmulationTask,
)
from src.emulator.constants import (
    AlarmCodes,
    AlarmPriorities,
    DeviceEmulationModes,
    DeviceEmulationNames,
    DeviceTypes,
)


class DeviceDataEmulator(abc.ABC):
    task_id: uuid.UUID
    patient_primary_identifier: str | None
    device_primary_identifier: str
    device_type: DeviceTypes
    mode: DeviceEmulationModes

    def __init__(
        self,
        patient_primary_identifier: str | None,
        device_primary_identifier: str,
        device_type: DeviceTypes,
        mode: Optional[DeviceEmulationModes] = None,
    ):
        self.task_id = uuid.uuid4()
        self.patient_primary_identifier = patient_primary_identifier
        self.device_primary_identifier = device_primary_identifier
        self.device_type = device_type
        self.mode = mode if mode is not None else self.initial_emulation_mode

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name for the data emulator"""

    @property
    @abc.abstractmethod
    def initial_emulation_mode(self) -> DeviceEmulationModes:
        """Emulation mode to start with"""

    @property
    @abc.abstractmethod
    def emulation_modes(self) -> Dict[DeviceEmulationModes, Type[EmulationTask]]:
        """Supported emulation modes"""

    @property
    @abc.abstractmethod
    def emulation_modes_alarms(
        self,
    ) -> Dict[DeviceEmulationModes, tuple[AlarmCodes, AlarmPriorities]]:
        """Alarms when each emulation mode is active"""

    async def __call__(self, mode: Optional[DeviceEmulationModes] = None):
        if mode is None:
            emulation_task = self.emulation_modes[self.initial_emulation_mode]
        else:
            emulation_task = self.emulation_modes[mode]
        return await emulation_task(
            self.patient_primary_identifier,
            self.device_primary_identifier,
            self.device_type,
        )()


class MonitorConnectionStatusEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.MONITOR_CONNECTION_STATUS
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.NORMAL: emulation_modes.NormalMonitorConnectionStatusEmulator,
        DeviceEmulationModes.ERROR: emulation_modes.ErrorMonitorConnectionStatusEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.ERROR: [],
    }


class BloodPressureEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.BLOOD_PRESSURE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowBloodPressureEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalBloodPressureEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.HighBloodPressureEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [
            (AlarmCodes.NIBP_SYS_LOW, AlarmPriorities.MEDIUM),
            (AlarmCodes.NIBP_SYS_LOW_AUDIO, AlarmPriorities.MEDIUM),
            (AlarmCodes.NIBP_DIA_LOW, AlarmPriorities.MEDIUM),
            (AlarmCodes.NIBP_DIA_LOW_AUDIO, AlarmPriorities.MEDIUM),
        ],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [
            (AlarmCodes.NIBP_SYS_HIGH, AlarmPriorities.MEDIUM),
            (AlarmCodes.NIBP_SYS_HIGH_AUDIO, AlarmPriorities.MEDIUM),
            (AlarmCodes.NIBP_DIA_HIGH, AlarmPriorities.MEDIUM),
            (AlarmCodes.NIBP_DIA_HIGH_AUDIO, AlarmPriorities.MEDIUM),
        ],
    }


class HeartRateEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.HEART_RATE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowHeartRateEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalHeartRateEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.HighHeartRateEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [
            (AlarmCodes.HR_LOW, AlarmPriorities.MEDIUM),
            (AlarmCodes.HR_LOW_AUDIO, AlarmPriorities.MEDIUM),
        ],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [
            (AlarmCodes.HR_HIGH, AlarmPriorities.MEDIUM),
            (AlarmCodes.HR_HIGH_AUDIO, AlarmPriorities.MEDIUM),
        ],
    }


class CardiacEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.CARDIAC
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowCardiacMetricsEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalCardiacMetricsEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.HighCardiacMetricsEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [
            (AlarmCodes.HR_LOW, AlarmPriorities.MEDIUM),
            (AlarmCodes.HR_LOW_AUDIO, AlarmPriorities.MEDIUM),
        ],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [
            (AlarmCodes.HR_HIGH, AlarmPriorities.MEDIUM),
            (AlarmCodes.HR_HIGH_AUDIO, AlarmPriorities.MEDIUM),
        ],
    }


class BloodOxygenEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.BLOOD_OXYGEN
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowBloodOxygenLevelEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalBloodOxygenEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [
            (AlarmCodes.SPO2_LOW, AlarmPriorities.MEDIUM),
            (AlarmCodes.SPO2_LOW_AUDIO, AlarmPriorities.MEDIUM),
        ],
        DeviceEmulationModes.NORMAL: [],
    }


class PulseEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.PULSE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowPulseEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalPulseEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.HighPulseEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [],
    }


class PulseRateEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.PULSE_RATE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowPulseRateEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalPulseRateEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.HighPulseRateEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [
            (AlarmCodes.PR_LOW, AlarmPriorities.MEDIUM),
            (AlarmCodes.PR_LOW_AUDIO, AlarmPriorities.MEDIUM),
        ],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [
            (AlarmCodes.PR_HIGH, AlarmPriorities.MEDIUM),
            (AlarmCodes.PR_HIGH_AUDIO, AlarmPriorities.MEDIUM),
        ],
    }


class PerfusionIndexEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.PERFUSION_INDEX
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.NORMAL: emulation_modes.NormalPerfusionIndexEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.NORMAL: [],
    }


class BodyTemperatureEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.BODY_TEMPERATURE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowBodyTemperatureEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalBodyTemperatureEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.HighBodyTemperatureEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [
            (AlarmCodes.BODY_TEMP_LOW, AlarmPriorities.MEDIUM),
            (AlarmCodes.BODY_TEMP_LOW_AUDIO, AlarmPriorities.MEDIUM),
        ],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [
            (AlarmCodes.BODY_TEMP_HIGH, AlarmPriorities.MEDIUM),
            (AlarmCodes.BODY_TEMP_HIGH_AUDIO, AlarmPriorities.MEDIUM),
        ],
    }


class ChestTemperatureEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.CHEST_TEMPERATURE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowChestTemperatureEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalChestTemperatureEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.HighChestTemperatureEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [
            (AlarmCodes.CHEST_SKIN_TEMP_LOW, AlarmPriorities.MEDIUM),
            (AlarmCodes.CHEST_SKIN_TEMP_LOW_AUDIO, AlarmPriorities.MEDIUM),
        ],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [
            (AlarmCodes.CHEST_SKIN_TEMP_HIGH, AlarmPriorities.MEDIUM),
            (AlarmCodes.CHEST_SKIN_TEMP_HIGH_AUDIO, AlarmPriorities.MEDIUM),
        ],
    }


class LimbTemperatureEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.LIMB_TEMPERATURE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowLimbTemperatureEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalLimbTemperatureEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.HighLimbTemperatureEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [
            (AlarmCodes.LIMB_SKIN_TEMP_LOW, AlarmPriorities.MEDIUM),
            (AlarmCodes.LIMB_SKIN_TEMP_LOW_AUDIO, AlarmPriorities.MEDIUM),
        ],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [
            (AlarmCodes.LIMB_SKIN_TEMP_HIGH, AlarmPriorities.MEDIUM),
            (AlarmCodes.LIMB_SKIN_TEMP_HIGH_AUDIO, AlarmPriorities.MEDIUM),
        ],
    }


class FallsEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.FALLS
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.NORMAL: emulation_modes.FallsZeroEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.FallsExistingEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [
            (AlarmCodes.FALL_DETECTED, AlarmPriorities.MEDIUM),
            (AlarmCodes.FALL_DETECTED_AUDIO, AlarmPriorities.MEDIUM),
        ],
    }


class PositionEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.POSITION
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.NORMAL: emulation_modes.NormalPositionEmulator,
        DeviceEmulationModes.FIXED: emulation_modes.HighPositionEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.FIXED: [
            (AlarmCodes.POSITION_DURATION_ALERT, AlarmPriorities.LOW),
            (AlarmCodes.POSITION_DURATION_ALERT_AUDIO, AlarmPriorities.LOW),
        ],
    }


class BodyAngleEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.BODY_ANGLE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.NORMAL: emulation_modes.NormalBodyAngleEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [],
    }


class RespiratoryRateEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.RESPIRATORY_RATE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowRespiratoryRateEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalRespiratoryRateEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.HighRespiratoryRateEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [
            (AlarmCodes.RR_LOW, AlarmPriorities.MEDIUM),
            (AlarmCodes.RR_LOW_AUDIO, AlarmPriorities.MEDIUM),
        ],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [
            (AlarmCodes.RR_HIGH, AlarmPriorities.MEDIUM),
            (AlarmCodes.RR_HIGH_AUDIO, AlarmPriorities.MEDIUM),
        ],
    }


class MeanArterialPressureEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.MEAN_ARTERIAL_PRESSURE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.NORMAL: emulation_modes.NormalMeanArterialPressureEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [],
    }


class PLETHEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.PLETH
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowPLETHEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalPLETHEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.HighPLETHEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [],
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.HIGH: [],
    }


class DeviceSignalEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.SENSOR_SIGNAL
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowDeviceSignalEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalDeviceSignalEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [(AlarmCodes.LOW_SIGNAL_ALERT, AlarmPriorities.LOW)],
        DeviceEmulationModes.NORMAL: [],
    }


class DeviceBatteryEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.SENSOR_BATTERY
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.LOW: emulation_modes.LowDeviceBatteryEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.NormalDeviceBatteryEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.LOW: [(AlarmCodes.LOW_BATTERY_ALERT, AlarmPriorities.LOW)],
        DeviceEmulationModes.NORMAL: [],
    }


class DeviceBatteryChargingStatusEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.SENSOR_BATTERY_CHARGING_STATE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.ERROR: emulation_modes.EmptyDeviceBatteryChargingStatusEmulator,
        DeviceEmulationModes.LOW: emulation_modes.DischargingDeviceBatteryChargingStatusEmulator,
        DeviceEmulationModes.NORMAL: emulation_modes.ChargingDeviceBatteryChargingStatusEmulator,
        DeviceEmulationModes.HIGH: emulation_modes.FullDeviceBatteryChargingStatusEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.FIXED: [],
    }


class DeviceModuleStateEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.SENSOR_MODULE_STATE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.NORMAL: emulation_modes.NormalDeviceModuleStatusEmulator,
        DeviceEmulationModes.ERROR: emulation_modes.ErrorDeviceModuleStatusEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.ERROR: [(AlarmCodes.SENSOR_FAILURE_ALERT, AlarmPriorities.HIGH)],
    }


class DeviceLeadStateEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.SENSOR_LEAD_STATE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.NORMAL: emulation_modes.NormalDeviceLeadEmulator,
        DeviceEmulationModes.ERROR: emulation_modes.ErrorDeviceLeadEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.ERROR: [(AlarmCodes.LEAD_OFF_ALERT, AlarmPriorities.LOW)],
    }


class DeviceContactStateEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.SENSOR_CONTACT_STATE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.NORMAL: emulation_modes.NormalDeviceContactEmulator,
        DeviceEmulationModes.ERROR: emulation_modes.ErrorDeviceContactEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.ERROR: [(AlarmCodes.POOR_SKIN_CONTACT_ALERT, AlarmPriorities.LOW)],
    }


class DeviceConnectionStateEmulator(DeviceDataEmulator):
    name = DeviceEmulationNames.SENSOR_CONNECTION_STATE
    initial_emulation_mode = DeviceEmulationModes.NORMAL
    emulation_modes = {
        DeviceEmulationModes.NORMAL: emulation_modes.NormalDeviceConnectionEmulator,
        DeviceEmulationModes.ERROR: emulation_modes.ErrorDeviceConnectionEmulator,
    }
    emulation_modes_alarms = {
        DeviceEmulationModes.NORMAL: [],
        DeviceEmulationModes.ERROR: [(AlarmCodes.LOOSE_SLEEVE_ALERT, AlarmPriorities.LOW)],
    }
