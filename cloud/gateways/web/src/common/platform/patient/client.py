from typing import Optional
from uuid import UUID

from starlette import status

from src.common.platform.bed.schemas import (
    PlatformBedResources,
    PlatformCreateBedBatch,
    PlatformDeleteBedBatch,
    PlatformUpdateBedBatch,
)
from src.common.platform.bed_group.schemas import (
    PlatformBatchAssignBeds,
    PlatformBedGroupBatchCreate,
    PlatformBedGroupResources,
    PlatformDeleteBedGroup,
)
from src.common.platform.common.http_base import BaseClient
from src.common.platform.patient.schemas import (
    CreatePatientSchema,
    DeletePatientSchema,
    PlatformDeletePatientAdmissionSchema,
    PlatformEHRPatientResources,
    PlatformEncounterPatientAdmissionSchema,
    PlatformGetPatientObservations,
    PlatformPatient,
    PlatformPatientObservationsResources,
    PlatformPatientPhysiologicalAlert,
    PlatformPatientResources,
    UpsertPatientSchema,
)
from src.settings import settings


class PatientPlatformClient(BaseClient):
    root_url: str = f"{settings.PATIENT_PLATFORM_BASE_URL}"

    async def get_patient_by_identifier(self, identifier: str) -> Optional[PlatformPatient]:
        response = await self.client.get(f"{self.root_url}/identifier/{identifier}")
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return None
        response.raise_for_status()
        return PlatformPatient.model_validate_json(response.text)

    async def get_patient_by_id(self, patient_id: UUID) -> Optional[PlatformPatient]:
        response = await self.client.get(f"{self.root_url}/{patient_id}")
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return None
        response.raise_for_status()
        return PlatformPatient.model_validate_json(response.text)

    async def get_patients(self) -> PlatformPatientResources:
        response = await self.client.get(self.root_url)
        response.raise_for_status()
        return PlatformPatientResources.model_validate_json(response.text)

    async def create_patient(self, patient: CreatePatientSchema) -> PlatformPatient:
        response = await self.client.post(
            f"{self.root_url}/CreatePatient",
            content=patient.model_dump_json(),
        )
        response.raise_for_status()
        return PlatformPatient.model_validate_json(response.text)

    async def update_patient(self, patient: UpsertPatientSchema) -> PlatformPatient:
        response = await self.client.post(
            f"{self.root_url}/UpdatePatientInfo",
            content=patient.model_dump_json(),
        )
        response.raise_for_status()
        return PlatformPatient.model_validate_json(response.text)

    async def batch_assign_beds(
        self,
        payload: PlatformBatchAssignBeds,
    ):
        response = await self.client.post(
            f"{self.root_url}/bed-group/BatchAssignBeds",
            content=payload.model_dump_json(),
        )
        response.raise_for_status()

    async def get_beds(self) -> PlatformBedResources:
        response = await self.client.get(f"{self.root_url}/bed")
        response.raise_for_status()

        return PlatformBedResources.model_validate_json(response.text)

    async def create_bed_batch(self, payload: PlatformCreateBedBatch) -> PlatformBedResources:
        response = await self.client.post(
            f"{self.root_url}/bed/BatchCreateBeds",
            content=payload.model_dump_json(),
        )

        response.raise_for_status()
        return PlatformBedResources.model_validate_json(response.text)

    async def update_bed_batch(self, payload: PlatformUpdateBedBatch) -> PlatformBedResources:
        response = await self.client.post(
            f"{self.root_url}/bed/BatchUpdateBeds",
            content=payload.model_dump_json(),
        )
        response.raise_for_status()
        return PlatformBedResources.model_validate_json(response.text)

    async def delete_bed_batch(self, payload: PlatformDeleteBedBatch):
        response = await self.client.post(
            f"{self.root_url}/bed/BatchDeleteBeds",
            content=payload.model_dump_json(),
        )
        response.raise_for_status()

    async def create_bed_group_batch(
        self, payload: PlatformBedGroupBatchCreate
    ) -> PlatformBedGroupResources:
        response = await self.client.post(
            f"{self.root_url}/bed-group/BatchCreateBedGroups",
            content=payload.model_dump_json(),
        )
        response.raise_for_status()
        return PlatformBedGroupResources.model_validate_json(response.text)

    async def update_bed_group_batch(self, payload: PlatformBedGroupBatchCreate) -> None:
        response = await self.client.post(
            f"{self.root_url}/bed-group/BatchUpdateBedGroups",
            content=payload.model_dump_json(),
        )
        response.raise_for_status()

    async def delete_bed_group_batch(self, payload: PlatformDeleteBedGroup):
        response = await self.client.post(
            f"{self.root_url}/bed-group/BatchDeleteBedGroups",
            content=payload.model_dump_json(),
        )
        response.raise_for_status()

    async def get_bed_groups(self) -> PlatformBedGroupResources:
        response = await self.client.get(f"{self.root_url}/bed-group")
        response.raise_for_status()
        return PlatformBedGroupResources.model_validate_json(response.text)

    async def delete_patient(self, payload: DeletePatientSchema):
        response = await self.client.post(
            f"{self.root_url}/DeletePatient", content=payload.model_dump_json()
        )
        response.raise_for_status()

    async def delete_patient_admission(self, payload: PlatformDeletePatientAdmissionSchema):
        response = await self.client.post(
            f"{self.root_url}/DismissPatientAdmission", content=payload.model_dump_json()
        )
        response.raise_for_status()

    async def get_assigned_beds_for_group(self, group_id: UUID) -> PlatformBedResources:
        response = await self.client.get(f"{self.root_url}/bed-group/{group_id}/beds")
        response.raise_for_status()
        return PlatformBedResources.model_validate_json(response.text)

    async def get_patients_observations(self, params: PlatformGetPatientObservations):
        if params is not None:
            params = params.model_dump(exclude_none=True)
        response = await self.client.get(url=f"{self.root_url}/observation", params=params)
        response.raise_for_status()
        return PlatformPatientObservationsResources.model_validate_json(response.text)

    async def get_session_alerts(self, patient_id: UUID) -> list[PlatformPatientPhysiologicalAlert]:
        response = await self.client.get(url=f"{self.root_url}/{patient_id}/session/alerts")
        response.raise_for_status()
        return [PlatformPatientPhysiologicalAlert(**x) for x in response.json()]

    async def encounter_patient_admission(
        self, payload: PlatformEncounterPatientAdmissionSchema
    ) -> None:
        response = await self.client.post(
            f"{self.root_url}/PlanPatientAdmission", content=payload.model_dump_json()
        )
        response.raise_for_status()


class EHRClient(BaseClient):
    root_url: str = f"{settings.EHR_PLATFORM_BASE_URL}"

    async def get_patients(self, params: dict[str, str]) -> PlatformEHRPatientResources:
        response = await self.client.get(url=f"{self.root_url}/query/patient/", params=params)
        response.raise_for_status()

        return PlatformEHRPatientResources.model_validate_json(response.text)
