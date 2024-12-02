from datetime import datetime
from typing import Any, Optional

from app.common.event_sourcing.events import Event
from app.common.models import AlertLog, Observation, Patient
from app.patient.schemas import (
    CreateObservationSchema,
    CreatePatientSchema,
    UpdatePatientSchema,
)


class CreatePatientEvent(Event[Patient]):
    display_name: str = "Patient Created"
    event_type: str = "PATIENT_CREATED_EVENT"

    def __init__(self, username: str, payload: CreatePatientSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, entity: Optional[Patient] = None) -> Patient:
        patient = Patient(
            id=self.payload.id,
            primary_identifier=self.payload.primary_identifier,
            active=self.payload.active,
            given_name=self.payload.given_name.get_secret_value(),
            family_name=self.payload.family_name.get_secret_value(),
            gender=self.payload.gender,
            birth_date=self.payload.birth_date.get_secret_value()
            if self.payload.birth_date
            else None,
        )
        return patient

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.payload.id,
            "primary_identifier": self.payload.primary_identifier,
            "active": self.payload.active,
            "given_name": self.payload.given_name.get_secret_value(),
            "family_name": self.payload.family_name.get_secret_value(),
            "gender": self.payload.gender,
            "birth_date": self.payload.birth_date.get_secret_value()
            if self.payload.birth_date
            else None,
        }


class UpdatePatientInfoEvent(Event[Patient]):
    display_name: str = "Patient personal information updated"
    event_type: str = "UPDATE_PATIENT_INFO_EVENT"

    def __init__(self, username: str, payload: UpdatePatientSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, entity: Patient) -> Patient:
        entity.primary_identifier = self.payload.primary_identifier
        entity.given_name = self.payload.given_name.get_secret_value()
        entity.family_name = self.payload.family_name.get_secret_value()
        entity.active = self.payload.active
        entity.gender = self.payload.gender
        entity.birth_date = (
            self.payload.birth_date.get_secret_value() if self.payload.birth_date else None
        )
        return entity

    def as_dict(self) -> dict[str, Any]:
        return {
            "primary_identifier": self.payload.primary_identifier,
            "active": self.payload.active,
            "given_name": self.payload.given_name.get_secret_value(),
            "family_name": self.payload.family_name.get_secret_value(),
            "gender": self.payload.gender,
            "birth_date": self.payload.birth_date.get_secret_value()
            if self.payload.birth_date
            else None,
        }


class DeletePatientEvent(Event[Patient]):
    display_name: str = "Patient Deleted"
    event_type: str = "PATIENT_DELETED_EVENT"

    def process(self, entity: Patient) -> Patient:
        return entity


class CreateObservationEvent(Event[Observation]):
    display_name: str = "Observation Created"
    event_type: str = "OBSERVATION_CREATED_EVENT"

    def __init__(self, username: str, payload: CreateObservationSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, entity: Optional[Observation] = None) -> Observation:
        observation = Observation(
            id=self.payload.id,
            category=self.payload.category,
            code=self.payload.code,
            subject_id=self.payload.subject_id,
            effective_dt=self.payload.effective_dt,
            value_text=self.payload.value_text,
            is_alert=self.payload.is_alert,
            device_primary_identifier=self.payload.device_primary_identifier,
            device_code=self.payload.device_code,
        )
        return observation

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.payload.id,
            "category": self.payload.category,
            "code": self.payload.code,
            "subject_id": self.payload.subject_id,
            "effective_dt": self.payload.effective_dt,
            "value_text": self.payload.value_text,
            "is_alert": self.payload.is_alert,
            "device_primary_identifier": self.payload.device_primary_identifier,
            "device_code": self.payload.device_code,
        }


class DeleteObservationEvent(Event[Observation]):
    display_name: str = "Observation Deleted"
    event_type: str = "OBSERVATION_DELETED_EVENT"

    def process(self, entity: Observation) -> Observation:
        return entity


class MultipleObservationsUpdatedEvent(Event[Observation]):
    display_name: str = "Multiple Observations Updated"
    event_type: str = "MULTIPLE_OBSERVATIONS_UPDATED"

    def process(self, entity: Observation) -> Observation:
        return entity


class ActivateAlertEvent(Event[AlertLog]):  # pylint: disable=too-many-instance-attributes
    display_name: str = "Alert activated"
    event_type: str = "ALERT_ACTIVATED_EVENT"

    def __init__(
        self,
        username: str,
        code: str,
        patient: Patient,
        determination_time: datetime,
        value_text: str,
        device_primary_identifier: str,
        device_code: str,
        trigger_upper_limit: Optional[float],
        trigger_lower_limit: Optional[float],
    ):  # pylint: disable=too-many-arguments
        super().__init__(username)
        self.code = code
        self.patient_id = patient.id
        self.patient_primary_identifier = patient.primary_identifier
        self.determination_time = determination_time
        self.value_text = value_text
        self.device_primary_identifier = device_primary_identifier
        self.device_code = device_code
        self.trigger_upper_limit = trigger_upper_limit
        self.trigger_lower_limit = trigger_lower_limit

    def process(self, entity: Optional[AlertLog] = None) -> AlertLog:
        alert = AlertLog(
            code=self.code,
            patient_id=self.patient_id,
            patient_primary_identifier=self.patient_primary_identifier,
            determination_time=self.determination_time,
            value_text=self.value_text,
            device_primary_identifier=self.device_primary_identifier,
            device_code=self.device_code,
            active=True,
            trigger_upper_limit=self.trigger_upper_limit,
            trigger_lower_limit=self.trigger_lower_limit,
        )
        return alert

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "patient_id": self.patient_id,
            "patient_primary_identifier": self.patient_primary_identifier,
            "determination_time": self.determination_time,
            "value_text": self.value_text,
            "device_primary_identifier": self.device_primary_identifier,
            "device_code": self.device_code,
            "active": True,
            "trigger_upper_limit": self.trigger_upper_limit,
            "trigger_lower_limit": self.trigger_lower_limit,
        }


class DeactivateAlertEvent(Event[AlertLog]):  # pylint: disable=too-many-instance-attributes
    display_name: str = "Alert deactivated"
    event_type: str = "ALERT_DEACTIVATED_EVENT"

    def __init__(
        self,
        username: str,
        code: str,
        patient: Patient,
        determination_time: datetime,
        value_text: str,
        device_primary_identifier: str,
        device_code: str,
        trigger_upper_limit: Optional[float],
        trigger_lower_limit: Optional[float],
    ):  # pylint: disable=too-many-arguments
        super().__init__(username)
        self.code = code
        self.patient_id = patient.id
        self.patient_primary_identifier = patient.primary_identifier
        self.determination_time = determination_time
        self.value_text = value_text
        self.device_primary_identifier = device_primary_identifier
        self.device_code = device_code
        self.trigger_upper_limit = trigger_upper_limit
        self.trigger_lower_limit = trigger_lower_limit

    def process(self, entity: Optional[AlertLog] = None) -> AlertLog:
        alert = AlertLog(
            code=self.code,
            patient_id=self.patient_id,
            patient_primary_identifier=self.patient_primary_identifier,
            determination_time=self.determination_time,
            value_text=self.value_text,
            device_primary_identifier=self.device_primary_identifier,
            device_code=self.device_code,
            active=False,
            trigger_upper_limit=self.trigger_upper_limit,
            trigger_lower_limit=self.trigger_lower_limit,
        )
        return alert

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "patient_id": self.patient_id,
            "patient_primary_identifier": self.patient_primary_identifier,
            "determination_time": self.determination_time,
            "value_text": self.value_text,
            "device_primary_identifier": self.device_primary_identifier,
            "device_code": self.device_code,
            "active": False,
            "trigger_upper_limit": self.trigger_upper_limit,
            "trigger_lower_limit": self.trigger_lower_limit,
        }
