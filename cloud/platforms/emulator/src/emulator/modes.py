import asyncio
from typing import Any, Dict, Generator, List

from src.emulator.base_modes import (
    BooleanEmulator,
    ConnectionStatusTask,
    EmulationTask,
    FloatMetricEmulator,
    IntegerMetricEmulator,
    StringEnumEmulator,
    TimerEmulator,
    WaveformEmulator,
)
from src.emulator.constants import ConnectionStatuses, SampleCodes, UnitCodes
from src.emulator.utils import generate_dataset_from_csv
from src.settings import settings

# TODO: Update with new dataset

BASE_ECG_DATA = generate_dataset_from_csv(settings.BASE_DIR / "datasets/ecg_demo.csv", "ecg", 40000)
LOW_ECG_DATA = BASE_ECG_DATA
NORMAL_ECG_DATA = BASE_ECG_DATA
HIGH_ECG_DATA = BASE_ECG_DATA


# TODO: Update with new dataset
BASE_PLETH_DATASET = generate_dataset_from_csv(settings.BASE_DIR / "datasets/ppg_demo.csv", "IR")
LOW_PLETH_DATASET = BASE_PLETH_DATASET
NORMAL_PLETH_DATASET = BASE_PLETH_DATASET
HIGH_PLETH_DATASET = BASE_PLETH_DATASET


# TODO: Update with new dataset
BASE_RR_DATASET = generate_dataset_from_csv(
    settings.BASE_DIR / "datasets/vitals_demo.csv", "RR(rpm)"
)
LOW_RR_DATASET = BASE_RR_DATASET
NORMAL_RR_DATASET = BASE_RR_DATASET
HIGH_RR_DATASET = BASE_RR_DATASET


class NormalMonitorConnectionStatusEmulator(ConnectionStatusTask):
    interval: float = float(settings.PM_CONNECTION_STATUS_MESSAGE_INTERVAL_IN_SECONDS)
    generated_value: bool = True


class ErrorMonitorConnectionStatusEmulator(ConnectionStatusTask):
    interval: float = float(settings.PM_CONNECTION_STATUS_MESSAGE_INTERVAL_IN_SECONDS)
    generated_value: bool = False


class LowDiastolicBloodPressureEmulator(IntegerMetricEmulator):
    interval: float = float(settings.BP_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 30
    max_value: int = 45
    step_value: int = 5
    sample_code: str = SampleCodes.DIA.value
    coded_value: str = UnitCodes.MERCURY_MILIMETRES.value


class NormalDiastolicBloodPressureEmulator(IntegerMetricEmulator):
    interval: float = float(settings.BP_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 70
    max_value: int = 100
    step_value: int = 5
    sample_code: str = SampleCodes.DIA.value
    coded_value: str = UnitCodes.MERCURY_MILIMETRES.value


class HighDiastolicBloodPressureEmulator(IntegerMetricEmulator):
    interval: float = float(settings.BP_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 125
    max_value: int = 140
    step_value: int = 5
    sample_code: str = SampleCodes.DIA.value
    coded_value: str = UnitCodes.MERCURY_MILIMETRES.value


class LowSystolicBloodPressureEmulator(IntegerMetricEmulator):
    interval: float = float(settings.BP_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 70
    max_value: int = 80
    step_value: int = 5
    sample_code: str = SampleCodes.SYS.value
    coded_value: str = UnitCodes.MERCURY_MILIMETRES.value


class NormalSystolicBloodPressureEmulator(IntegerMetricEmulator):
    interval: float = float(settings.BP_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 120
    max_value: int = 140
    step_value: int = 5
    sample_code: str = SampleCodes.SYS.value
    coded_value: str = UnitCodes.MERCURY_MILIMETRES.value


class HighSystolicBloodPressureEmulator(IntegerMetricEmulator):
    interval: float = float(settings.BP_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 165
    max_value: int = 180
    step_value: int = 5
    sample_code: str = SampleCodes.SYS.value
    coded_value: str = UnitCodes.MERCURY_MILIMETRES.value


class LowBloodPressureEmulator(EmulationTask):
    interval: float = float(settings.BP_MESSAGE_INTERVAL_IN_SECONDS)

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Dict[str, Any]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            LowDiastolicBloodPressureEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            LowSystolicBloodPressureEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class NormalBloodPressureEmulator(EmulationTask):
    interval: float = float(settings.BP_MESSAGE_INTERVAL_IN_SECONDS)

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Dict[str, Any]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            NormalDiastolicBloodPressureEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            NormalSystolicBloodPressureEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class HighBloodPressureEmulator(EmulationTask):
    interval: float = float(settings.BP_MESSAGE_INTERVAL_IN_SECONDS)

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Dict[str, Any]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            HighDiastolicBloodPressureEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            HighSystolicBloodPressureEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class LowHeartRateEmulator(IntegerMetricEmulator):
    interval: float = float(settings.HR_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 30
    max_value: int = 40
    sample_code: str = SampleCodes.HR.value
    coded_value: str = UnitCodes.BEATS_PER_MINUTE.value


class NormalHeartRateEmulator(IntegerMetricEmulator):
    interval: float = float(settings.HR_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 60
    max_value: int = 70
    sample_code: str = SampleCodes.HR.value
    coded_value: str = UnitCodes.BEATS_PER_MINUTE.value


class HighHeartRateEmulator(IntegerMetricEmulator):
    interval: float = float(settings.HR_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 130
    max_value: int = 135
    sample_code: str = SampleCodes.HR.value
    coded_value: str = UnitCodes.BEATS_PER_MINUTE.value


class LowHeartRateECGEmulator(WaveformEmulator):
    dataset = LOW_ECG_DATA
    interval: float = float(settings.ECG_MESSAGE_INTERVAL_IN_SECONDS)
    max_samples = int(settings.ECG_MAXIMUM_DATAPOINTS_PER_SECOND * interval)
    sample_code: str = SampleCodes.ECG.value
    sample_period: float = float(1 / settings.ECG_MAXIMUM_DATAPOINTS_PER_SECOND)
    determination_period: float = float(settings.ECG_MESSAGE_INTERVAL_IN_SECONDS)


class NormalHeartRateECGEmulator(WaveformEmulator):
    dataset = NORMAL_ECG_DATA
    interval: float = float(settings.ECG_MESSAGE_INTERVAL_IN_SECONDS)
    max_samples = int(settings.ECG_MAXIMUM_DATAPOINTS_PER_SECOND * interval)
    sample_code: str = SampleCodes.ECG.value
    sample_period: float = float(1 / settings.ECG_MAXIMUM_DATAPOINTS_PER_SECOND)
    determination_period: float = float(settings.ECG_MESSAGE_INTERVAL_IN_SECONDS)


class HighHeartRateECGEmulator(WaveformEmulator):
    dataset = HIGH_ECG_DATA
    interval: float = float(settings.ECG_MESSAGE_INTERVAL_IN_SECONDS)
    max_samples = int(settings.ECG_MAXIMUM_DATAPOINTS_PER_SECOND * interval)
    sample_code: str = SampleCodes.ECG.value
    sample_period: float = float(1 / settings.ECG_MAXIMUM_DATAPOINTS_PER_SECOND)
    determination_period: float = float(settings.ECG_MESSAGE_INTERVAL_IN_SECONDS)


class LowCardiacMetricsEmulator(EmulationTask):
    interval: float = float(settings.HR_MESSAGE_INTERVAL_IN_SECONDS)

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Dict[str, Any]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            LowHeartRateEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            LowHeartRateECGEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class NormalCardiacMetricsEmulator(EmulationTask):
    interval: float = float(settings.HR_MESSAGE_INTERVAL_IN_SECONDS)

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Dict[str, Any]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            NormalHeartRateEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            NormalHeartRateECGEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class HighCardiacMetricsEmulator(EmulationTask):
    interval: float = float(settings.HR_MESSAGE_INTERVAL_IN_SECONDS)

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Dict[str, Any]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            HighHeartRateEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            HighHeartRateECGEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class LowBloodOxygenLevelEmulator(IntegerMetricEmulator):
    interval: float = float(settings.SPO2_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 70
    max_value: int = 80
    sample_code: str = SampleCodes.SPO2.value
    coded_value: str = UnitCodes.PERCENTAGE.value


class NormalBloodOxygenEmulator(IntegerMetricEmulator):
    interval: float = float(settings.SPO2_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 96
    max_value: int = 99
    sample_code: str = SampleCodes.SPO2.value
    coded_value: str = UnitCodes.PERCENTAGE.value


class LowPulseEmulator(IntegerMetricEmulator):
    interval: float = float(settings.PULSE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 35
    max_value: int = 40
    sample_code: str = SampleCodes.PULSE.value
    coded_value: str = UnitCodes.BEATS_PER_MINUTE.value


class NormalPulseEmulator(IntegerMetricEmulator):
    interval: float = float(settings.PULSE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 60
    max_value: int = 70
    sample_code: str = SampleCodes.PULSE.value
    coded_value: str = UnitCodes.BEATS_PER_MINUTE.value


class HighPulseEmulator(IntegerMetricEmulator):
    interval: float = float(settings.PULSE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 130
    max_value: int = 135
    sample_code: str = SampleCodes.PULSE.value
    coded_value: str = UnitCodes.BEATS_PER_MINUTE.value


class LowPulseRateEmulator(IntegerMetricEmulator):
    interval: float = float(settings.PR_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 35
    max_value: int = 40
    sample_code: str = SampleCodes.PR.value
    coded_value: str = UnitCodes.BEATS_PER_MINUTE.value


class NormalPulseRateEmulator(IntegerMetricEmulator):
    interval: float = float(settings.PR_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 60
    max_value: int = 70
    sample_code: str = SampleCodes.PR.value
    coded_value: str = UnitCodes.BEATS_PER_MINUTE.value


class HighPulseRateEmulator(IntegerMetricEmulator):
    interval: float = float(settings.PR_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 130
    max_value: int = 135
    sample_code: str = SampleCodes.PR.value
    coded_value: str = UnitCodes.BEATS_PER_MINUTE.value


class NormalPerfusionIndexEmulator(FloatMetricEmulator):
    interval: float = float(settings.PI_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 10.0
    max_value: float = 15.0
    sample_code: str = SampleCodes.PI.value
    coded_value: str = UnitCodes.PERCENTAGE.value


class LowBodyTemperatureEmulator(FloatMetricEmulator):
    interval: float = float(settings.TEMPERATURE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 91.1
    max_value: float = 92.7
    step_value: float = 0.2
    sample_code: str = SampleCodes.BODY_TEMP.value
    coded_value: str = UnitCodes.FAHRENHEIT.value


class NormalBodyTemperatureEmulator(FloatMetricEmulator):
    interval: float = float(settings.TEMPERATURE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 96.6
    max_value: float = 98.2
    step_value: float = 0.2
    sample_code: str = SampleCodes.BODY_TEMP.value
    coded_value: str = UnitCodes.FAHRENHEIT.value


class HighBodyTemperatureEmulator(FloatMetricEmulator):
    interval: float = float(settings.TEMPERATURE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 102.5
    max_value: float = 104.5
    step_value: float = 0.2
    sample_code: str = SampleCodes.BODY_TEMP.value
    coded_value: str = UnitCodes.FAHRENHEIT.value


class LowChestTemperatureEmulator(FloatMetricEmulator):
    interval: float = float(settings.TEMPERATURE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 91.1
    max_value: float = 92.7
    step_value: float = 0.2
    sample_code: str = SampleCodes.CHEST_TEMP.value
    coded_value: str = UnitCodes.FAHRENHEIT.value


class NormalChestTemperatureEmulator(FloatMetricEmulator):
    interval: float = float(settings.TEMPERATURE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 96.8
    max_value: float = 98.4
    step_value: float = 0.2
    sample_code: str = SampleCodes.CHEST_TEMP.value
    coded_value: str = UnitCodes.FAHRENHEIT.value


class HighChestTemperatureEmulator(FloatMetricEmulator):
    interval: float = float(settings.TEMPERATURE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 102.5
    max_value: float = 104.5
    step_value: float = 0.2
    sample_code: str = SampleCodes.CHEST_TEMP.value
    coded_value: str = UnitCodes.FAHRENHEIT.value


class LowLimbTemperatureEmulator(FloatMetricEmulator):
    interval: float = float(settings.TEMPERATURE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 91.1
    max_value: float = 92.7
    step_value: float = 0.2
    sample_code: str = SampleCodes.LIMB_TEMP.value
    coded_value: str = UnitCodes.FAHRENHEIT.value


class NormalLimbTemperatureEmulator(FloatMetricEmulator):
    interval: float = float(settings.TEMPERATURE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 96.9
    max_value: float = 98.5
    step_value: float = 0.2
    sample_code: str = SampleCodes.LIMB_TEMP.value
    coded_value: str = UnitCodes.FAHRENHEIT.value


class HighLimbTemperatureEmulator(FloatMetricEmulator):
    interval: float = float(settings.TEMPERATURE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 102.5
    max_value: float = 104.5
    step_value: float = 0.2
    sample_code: str = SampleCodes.LIMB_TEMP.value
    coded_value: str = UnitCodes.FAHRENHEIT.value


class FallsZeroEmulator(IntegerMetricEmulator):
    interval: float = float(settings.FALLS_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 0
    max_value: int = 0
    sample_code: str = SampleCodes.FALLS.value
    coded_value: str = UnitCodes.NO_UNIT.value


class FallsExistingEmulator(IntegerMetricEmulator):
    interval: float = float(settings.FALLS_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 1
    max_value: int = 2
    sample_code: str = SampleCodes.FALLS.value
    coded_value: str = UnitCodes.NO_UNIT.value


class StaticPositionEmulator(StringEnumEmulator):
    interval: float = float(settings.POSITION_MESSAGE_INTERVAL_IN_SECONDS)
    sample_code: str = SampleCodes.POSITION.value
    coded_value: str = UnitCodes.NO_UNIT.value

    def get_values(self) -> List[str]:
        return ["SUPINE"]


class ChangePositionEmulator(StringEnumEmulator):
    interval: float = float(settings.POSITION_MESSAGE_INTERVAL_IN_SECONDS)
    sample_code: str = SampleCodes.POSITION.value
    coded_value: str = UnitCodes.NO_UNIT.value

    def get_values(self) -> List[str]:
        return ["SUPINE", "PRONE", "LEFT", "RIGHT", "UPRIGHT"]


class NormalPositionDurationEmulator(TimerEmulator):
    interval: float = float(settings.POSITION_DURATION_MESSAGE_INTERVAL_IN_SECONDS)
    start_value: int = 5
    max_value: int = 90
    sample_code: str = SampleCodes.POSITION_DURATION.value
    coded_value: str = UnitCodes.TIME.value


class HighPositionDurationEmulator(TimerEmulator):
    interval: float = float(settings.POSITION_DURATION_MESSAGE_INTERVAL_IN_SECONDS)
    start_value: int = 220
    max_value: int = 900
    sample_code: str = SampleCodes.POSITION_DURATION.value
    coded_value: str = UnitCodes.TIME.value


class NormalPositionEmulator(EmulationTask):
    interval: float = float(settings.POSITION_DURATION_MESSAGE_INTERVAL_IN_SECONDS)

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Dict[str, Any]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            ChangePositionEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            NormalPositionDurationEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class HighPositionEmulator(EmulationTask):
    interval: float = float(settings.POSITION_DURATION_MESSAGE_INTERVAL_IN_SECONDS)

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Dict[str, Any]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            StaticPositionEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            HighPositionDurationEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class NormalBodyAngleEmulator(IntegerMetricEmulator):
    interval: float = float(settings.BODY_ANGLE_INTERVAL_IN_SECONDS)
    min_value: int = 40
    max_value: int = 45
    sample_code: str = SampleCodes.BODY_ANGLE.value
    coded_value: str = UnitCodes.ANGLE.value


class LowRespiratoryRateMetricEmulator(IntegerMetricEmulator):
    interval: float = float(settings.RR_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 2
    max_value: int = 4
    step_value: int = 1
    sample_code: str = SampleCodes.RR_METRIC.value
    coded_value: str = UnitCodes.BREATHS_PER_MINUTE.value


class NormalRespiratoryRateMetricEmulator(IntegerMetricEmulator):
    interval: float = float(settings.RR_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 12
    max_value: int = 15
    step_value: int = 1
    sample_code: str = SampleCodes.RR_METRIC.value
    coded_value: str = UnitCodes.BREATHS_PER_MINUTE.value


class HighRespiratoryRateMetricEmulator(IntegerMetricEmulator):
    interval: float = float(settings.RR_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = 32
    max_value: int = 35
    step_value: int = 1
    sample_code: str = SampleCodes.RR_METRIC.value
    coded_value: str = UnitCodes.BREATHS_PER_MINUTE.value


class LowRespiratoryRateWF(WaveformEmulator):
    sample_code = SampleCodes.RR.value
    dataset = LOW_RR_DATASET
    interval = float(settings.RR_MESSAGE_INTERVAL_IN_SECONDS)
    max_samples = int(settings.RR_MAXIMUM_DATAPOINTS_PER_SECOND * interval)
    sample_period: float = float(1 / settings.RR_MAXIMUM_DATAPOINTS_PER_SECOND)
    determination_period: float = float(settings.RR_MESSAGE_INTERVAL_IN_SECONDS)


class NormalRespiratoryRateWF(WaveformEmulator):
    sample_code = SampleCodes.RR.value
    dataset = NORMAL_RR_DATASET
    interval = float(settings.RR_MESSAGE_INTERVAL_IN_SECONDS)
    max_samples = int(settings.RR_MAXIMUM_DATAPOINTS_PER_SECOND * interval)
    sample_period: float = float(1 / settings.RR_MAXIMUM_DATAPOINTS_PER_SECOND)
    determination_period: float = float(settings.RR_MESSAGE_INTERVAL_IN_SECONDS)


class HighRespiratoryRateWF(WaveformEmulator):
    sample_code = SampleCodes.RR.value
    dataset = HIGH_RR_DATASET
    interval = float(settings.RR_MESSAGE_INTERVAL_IN_SECONDS)
    max_samples = int(settings.RR_MAXIMUM_DATAPOINTS_PER_SECOND * interval)
    sample_period: float = float(1 / settings.RR_MAXIMUM_DATAPOINTS_PER_SECOND)
    determination_period: float = float(settings.RR_MESSAGE_INTERVAL_IN_SECONDS)


class LowRespiratoryRateEmulator(EmulationTask):
    interval = None

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Generator[Any, None, None]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            LowRespiratoryRateMetricEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            LowRespiratoryRateWF(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class NormalRespiratoryRateEmulator(EmulationTask):
    interval = None

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Generator[Any, None, None]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            NormalRespiratoryRateMetricEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            NormalRespiratoryRateWF(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class HighRespiratoryRateEmulator(EmulationTask):
    interval = None

    def get_emulated_message(self, value: Any) -> Dict[str, Any]:
        """Ignore"""

    def get_values_generator(self) -> Generator[Any, None, None]:
        """Ignore"""

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            HighRespiratoryRateMetricEmulator(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
            HighRespiratoryRateWF(
                self.patient_primary_identifier,
                self.device_primary_identifier,
                self.device_type,
            )(*args, **kwargs),
        )


class NormalMeanArterialPressureEmulator(IntegerMetricEmulator):
    interval: float = float(settings.MEAN_ARTERIAL_PRESSURE_INTERVAL_IN_SECONDS)
    min_value: int = 100
    max_value: int = 130
    sample_code: str = SampleCodes.MEAN_ARTERIAL_PRESSURE.value
    coded_value: str = UnitCodes.MERCURY_MILIMETRES.value


class LowPLETHEmulator(WaveformEmulator):
    sample_code = SampleCodes.PLETH.value
    dataset = LOW_PLETH_DATASET
    interval = float(settings.PLETH_MESSAGE_INTERVAL_IN_SECONDS)
    max_samples = int(settings.PLETH_MAXIMUM_DATAPOINTS_PER_SECOND * interval)
    sample_period: float = float(1 / settings.PLETH_MAXIMUM_DATAPOINTS_PER_SECOND)
    determination_period: float = float(settings.PLETH_MESSAGE_INTERVAL_IN_SECONDS)


class NormalPLETHEmulator(WaveformEmulator):
    sample_code = SampleCodes.PLETH.value
    dataset = NORMAL_PLETH_DATASET
    interval = float(settings.PLETH_MESSAGE_INTERVAL_IN_SECONDS)
    max_samples = int(settings.PLETH_MAXIMUM_DATAPOINTS_PER_SECOND * interval)
    sample_period: float = float(1 / settings.PLETH_MAXIMUM_DATAPOINTS_PER_SECOND)
    determination_period: float = float(settings.PLETH_MESSAGE_INTERVAL_IN_SECONDS)


class HighPLETHEmulator(WaveformEmulator):
    sample_code = SampleCodes.PLETH.value
    dataset = HIGH_PLETH_DATASET
    interval = float(settings.PLETH_MESSAGE_INTERVAL_IN_SECONDS)
    max_samples = int(settings.PLETH_MAXIMUM_DATAPOINTS_PER_SECOND * interval)
    sample_period: float = float(1 / settings.PLETH_MAXIMUM_DATAPOINTS_PER_SECOND)
    determination_period: float = float(settings.PLETH_MESSAGE_INTERVAL_IN_SECONDS)


class LowDeviceSignalEmulator(IntegerMetricEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = -100
    max_value: int = -93
    step_value: int = 2
    sample_code: str = SampleCodes.DEVICE_SIGNAL.value
    coded_value: str = UnitCodes.NO_UNIT.value


class NormalDeviceSignalEmulator(IntegerMetricEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: int = -80
    max_value: int = 0
    step_value: int = 5
    sample_code: str = SampleCodes.DEVICE_SIGNAL.value
    coded_value: str = UnitCodes.NO_UNIT.value


class LowDeviceBatteryEmulator(FloatMetricEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 0.05
    max_value: float = 0.2
    step_value: float = 0.05
    round_value: int = 2
    sample_code: str = SampleCodes.DEVICE_BATTERY.value
    coded_value: str = UnitCodes.PERCENTAGE.value


class NormalDeviceBatteryEmulator(FloatMetricEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    min_value: float = 0.6
    max_value: float = 1.0
    step_value: float = 0.05
    round_value: int = 2
    sample_code: str = SampleCodes.DEVICE_BATTERY.value
    coded_value: str = UnitCodes.PERCENTAGE.value


class EmptyDeviceBatteryChargingStatusEmulator(StringEnumEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    sample_code: str = SampleCodes.DEVICE_BATTERY_STATUS.value
    coded_value: str = UnitCodes.NO_UNIT.value

    def get_values(self) -> List[str]:
        return ["DEB"]


class DischargingDeviceBatteryChargingStatusEmulator(StringEnumEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    sample_code: str = SampleCodes.DEVICE_BATTERY_STATUS.value
    coded_value: str = UnitCodes.NO_UNIT.value

    def get_values(self) -> List[str]:
        return ["DisChB"]


class ChargingDeviceBatteryChargingStatusEmulator(StringEnumEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    sample_code: str = SampleCodes.DEVICE_BATTERY_STATUS.value
    coded_value: str = UnitCodes.NO_UNIT.value

    def get_values(self) -> List[str]:
        return ["ChB"]


class FullDeviceBatteryChargingStatusEmulator(StringEnumEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    sample_code: str = SampleCodes.DEVICE_BATTERY_STATUS.value
    coded_value: str = UnitCodes.NO_UNIT.value

    def get_values(self) -> List[str]:
        return ["Ful"]


class NormalDeviceModuleStatusEmulator(BooleanEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    fixed_status: bool = True
    sample_code: str = SampleCodes.DEVICE_MODULE.value
    coded_value: str = UnitCodes.NO_UNIT.value


class ErrorDeviceModuleStatusEmulator(BooleanEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    fixed_status: bool = False
    sample_code: str = SampleCodes.DEVICE_MODULE.value
    coded_value: str = UnitCodes.NO_UNIT.value


class NormalDeviceLeadEmulator(BooleanEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    fixed_status: bool = True
    sample_code: str = SampleCodes.DEVICE_LEAD.value
    coded_value: str = UnitCodes.NO_UNIT.value


class ErrorDeviceLeadEmulator(BooleanEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    fixed_status: bool = False
    sample_code: str = SampleCodes.DEVICE_LEAD.value
    coded_value: str = UnitCodes.NO_UNIT.value


class NormalDeviceContactEmulator(BooleanEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    fixed_status: bool = True
    sample_code: str = SampleCodes.DEVICE_CONTACT.value
    coded_value: str = UnitCodes.NO_UNIT.value


class ErrorDeviceContactEmulator(BooleanEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    fixed_status: bool = False
    sample_code: str = SampleCodes.DEVICE_CONTACT.value
    coded_value: str = UnitCodes.NO_UNIT.value


class NormalDeviceConnectionEmulator(BooleanEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    fixed_status: bool = True
    sample_code: str = ConnectionStatuses.CONNECTED.value
    coded_value: str = UnitCodes.NO_UNIT.value


class ErrorDeviceConnectionEmulator(BooleanEmulator):
    interval: float = float(settings.DEVICE_MESSAGE_INTERVAL_IN_SECONDS)
    fixed_status: bool = True
    sample_code: str = ConnectionStatuses.CONNECTION_LOST.value
    coded_value: str = UnitCodes.NO_UNIT.value
