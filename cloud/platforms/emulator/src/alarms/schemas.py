from typing import List, Optional

from pydantic import BaseModel

from src.emulator.constants import (
    AlarmCodes,
    AlarmPriorities,
    DeviceTypes,
    RangeCodes,
)


class AlarmRange(BaseModel):
    code: str = "0001"
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None
    alert_condition_enabled: bool = True


class AlarmPayload(BaseModel):
    patient_primary_identifier: str
    code: AlarmCodes
    priority: AlarmPriorities
    description: str
    device_code: DeviceTypes
    device_primary_identifier: str
    active: bool
    determination_time: Optional[float]
    vital_range: Optional[AlarmRange] = None
    latching: Optional[bool] = False


class TechnicalAlarmPayload(BaseModel):
    patient_primary_identifier: str
    device_primary_identifier: str
    code: AlarmCodes
    priority: AlarmPriorities
    device_code: DeviceTypes
    active: bool
    determination_time: Optional[float]
    vital_range: Optional[AlarmRange] = None


class DeviceRange(BaseModel):
    code: RangeCodes
    lower_limit: Optional[float]
    upper_limit: Optional[float]
    alert_condition_enabled: bool = True

    class Config:
        use_enum_values = True

    def to_dict(self) -> dict:
        return {
            "code": str(self.code),
            "lower_limit": self.lower_limit,
            "upper_limit": self.upper_limit,
            "alert_condition_enabled": self.alert_condition_enabled,
        }


class DeviceRangesPayload(BaseModel):
    primary_identifier: str
    ranges: List[DeviceRange]

    class Config:
        use_enum_values = True
