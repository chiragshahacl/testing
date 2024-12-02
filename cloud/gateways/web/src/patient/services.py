from typing import Any, Optional, Tuple
from uuid import UUID

import httpx
from fastapi import Depends

from cache import RedisCache
from src.common import schemas as common_schemas
from src.common.dependencies import PlatformHttpClient
from src.common.exceptions import BaseValidationException
from src.common.platform.device.client import DevicePlatformClient
from src.common.platform.patient.client import EHRClient, PatientPlatformClient
from src.common.platform.patient.schemas import (
    CreatePatientSchema,
    DeletePatientSchema,
    EHRPatient,
    PlatformDeletePatientAdmissionSchema,
    PlatformEHRPatientResources,
    PlatformEncounterPatientAdmissionSchema,
    PlatformGetEHRPatientParams,
    PlatformPatient,
    UpsertPatientSchema,
)
from src.patient import schemas as web_patient_schemas
from src.settings import settings


class PatientAlreadyMonitoredError(BaseValidationException):
    def __init__(self) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body"],
            msg="Patient is already being monitored.",
            type="value_error.patient_already_monitored",
        )


class SharedCache:
    def __init__(self):
        self.client = RedisCache()

    def _get(self, key: str) -> Any:
        value = self.client.get(f"{settings.REDIS_SHARED_CACHE_PREFIX}/{key}", parse=False)
        return value

    def patient_has_live_session(self, patient_primary_identifier: str) -> bool:
        return bool(self._get(patient_primary_identifier))


class PatientService:
    def __init__(self, http_client: httpx.AsyncClient = Depends(PlatformHttpClient())):
        self.http_client = http_client
        self.patient_client = PatientPlatformClient(self.http_client)

    async def _get_patient(self, identifier: str) -> Optional[PlatformPatient]:
        patient = await self.patient_client.get_patient_by_identifier(identifier)
        return patient

    async def get_patient(self, patient_id: UUID) -> Optional[web_patient_schemas.WebPatient]:
        patient = await self.patient_client.get_patient_by_id(patient_id)
        if not patient:
            return None
        return web_patient_schemas.WebPatient.from_platform(patient)

    async def get_patients(self) -> web_patient_schemas.WebPatientResources:
        patients = await self.patient_client.get_patients()
        return web_patient_schemas.WebPatientResources.from_platform(patients)

    async def create_patient(self, patient_payload: CreatePatientSchema) -> PlatformPatient:
        patient = await self.patient_client.create_patient(patient_payload)
        return patient

    async def create_or_update_patient(
        self, patient_payload: UpsertPatientSchema
    ) -> Tuple[PlatformPatient, bool]:
        identifier = patient_payload.primary_identifier
        found_patient = await self._get_patient(identifier)
        if not found_patient:
            patient = await self.patient_client.create_patient(patient_payload)
            created = True
        else:
            patient_payload.id = found_patient.id
            patient = await self.patient_client.update_patient(patient_payload)
            created = False
        return patient, created

    async def delete_patient(
        self,
        patient_id: UUID,
    ):
        payload = DeletePatientSchema.model_construct(id=patient_id)
        await self.patient_client.delete_patient(payload)

    async def delete_patient_admission(
        self,
        patient_id: UUID,
    ):
        payload = PlatformDeletePatientAdmissionSchema.model_construct(patient_id=patient_id)
        await self.patient_client.delete_patient_admission(payload)

    async def encounter_patient_admission(
        self, payload: web_patient_schemas.WebPatientAdmission
    ) -> None:
        upsert_payload = payload.payload.to_upsert_patient_payload()
        shared_cache = SharedCache()
        if shared_cache.patient_has_live_session(upsert_payload.primary_identifier):
            raise PatientAlreadyMonitoredError

        patient, _ = await self.create_or_update_patient(upsert_payload)
        payload = PlatformEncounterPatientAdmissionSchema.model_construct(
            subject_id=patient.id, bed_id=payload.bed_id
        )
        await self.patient_client.encounter_patient_admission(payload)


class SessionAlertsService:
    def __init__(self, http_client: httpx.AsyncClient = Depends(PlatformHttpClient())):
        self.http_client = http_client
        self.patient_client = PatientPlatformClient(self.http_client)
        self.device_client = DevicePlatformClient(self.http_client)

    async def get_session_alerts(
        self, patient_id: UUID
    ) -> web_patient_schemas.WebSessionAlertResources:
        alerts = await self.patient_client.get_session_alerts(patient_id)
        alerts = sorted(alerts, key=lambda k: k.start_determination_time, reverse=True)
        return web_patient_schemas.WebSessionAlertResources(resources=alerts)


def _split_patients_by_monitoring_status(
    resources: PlatformEHRPatientResources,
) -> tuple[list[EHRPatient], list[EHRPatient]]:
    monitored = []
    non_monitored = []
    shared_cache = SharedCache()
    for patient in resources.resources:
        if shared_cache.patient_has_live_session(patient.patient_primary_identifier):
            monitored.append(patient)
        else:
            non_monitored.append(patient)
    return monitored, non_monitored


class EHRService:
    def __init__(self, http_client: httpx.AsyncClient = Depends(PlatformHttpClient())):
        self.http_client = http_client
        self.ehr_client = EHRClient(self.http_client)

    async def get_ehr_patients(
        self, params: PlatformGetEHRPatientParams
    ) -> PlatformEHRPatientResources:
        if params is not None:
            params = params.model_dump(exclude_none=True, by_alias=True)
        ehr_resources = await self.ehr_client.get_patients(params)
        monitored_patients, non_monitored_patients = _split_patients_by_monitoring_status(
            ehr_resources
        )
        if monitored_patients and not non_monitored_patients:
            raise PatientAlreadyMonitoredError
        return PlatformEHRPatientResources.model_construct(
            resources=non_monitored_patients,
        )
