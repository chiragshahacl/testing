from uuid import UUID

import httpx
from fastapi import Depends

from src.bed import schemas as web_bed_schemas
from src.bed_group import schemas as web_bed_group_schemas
from src.common.dependencies import PlatformHttpClient
from src.common.platform.patient.client import PatientPlatformClient
from src.patient import schemas as web_patient_schemas


class BedGroupService:
    def __init__(self, http_client: httpx.AsyncClient = Depends(PlatformHttpClient())):
        self.http_client = http_client
        self.patient_client = PatientPlatformClient(self.http_client)

    async def batch_create_bed_groups(
        self, payload: web_bed_group_schemas.WebBedGroupCreateResources
    ) -> web_bed_group_schemas.WebBedGroupResources:
        bed_groups = await self.patient_client.create_bed_group_batch(payload.to_platform())
        return web_bed_group_schemas.WebBedGroupResources.from_platform(bed_groups)

    async def batch_delete_bed_groups(
        self, payload: web_bed_group_schemas.WebBedGroupBatchDelete
    ) -> None:
        await self.patient_client.delete_bed_group_batch(payload.to_platform())

    async def get_bed_groups(self) -> web_bed_group_schemas.WebBedGroupResources:
        platform_bed_group_resources = await self.patient_client.get_bed_groups()
        return web_bed_group_schemas.WebBedGroupResources.from_platform(
            platform_bed_group_resources
        )

    async def batch_assign_beds(self, payload: web_bed_group_schemas.WebBatchAssignBeds) -> None:
        await self.patient_client.batch_assign_beds(payload.to_platform())

    async def get_assigned_beds_for_group(self, group_id: UUID) -> web_bed_schemas.WebBedResources:
        platform_bed_resources = await self.patient_client.get_assigned_beds_for_group(group_id)
        return web_bed_schemas.WebBedResources.from_platform(platform_bed_resources)

    async def batch_create_or_update_bed_groups(
        self, payload: web_bed_group_schemas.WebBatchCreateOrUpdateBedGroup
    ):
        found_bed_groups = await self.patient_client.get_bed_groups()
        bed_groups_map = {bed_group.id: bed_group for bed_group in found_bed_groups.resources}
        bed_groups_to_create = []
        bed_groups_to_update = []
        for bed_group in payload.resources:
            if not bed_group.id or bed_group.id not in bed_groups_map:
                bed_groups_to_create.append(bed_group)
            else:
                current_state = bed_groups_map[bed_group.id]
                if (
                    bed_group.name != current_state.name
                    or bed_group.description != current_state.description
                ):
                    bed_groups_to_update.append(bed_group)
        if bed_groups_to_update:
            await self.patient_client.update_bed_group_batch(
                web_bed_group_schemas.WebBatchCreateOrUpdateBedGroup.to_platform_batch_update(
                    bed_groups_to_update
                )
            )
        if bed_groups_to_create:
            await self.patient_client.create_bed_group_batch(
                web_bed_group_schemas.WebBatchCreateOrUpdateBedGroup.to_platform_batch_create(
                    bed_groups_to_create
                )
            )

    async def get_bed_group_observations(
        self, bed_group_id: UUID
    ) -> web_bed_group_schemas.WebBedGroupAlertResources:
        beds = await self.get_assigned_beds_for_group(bed_group_id)
        patients_by_id = {str(bed.patient.id): bed.patient for bed in beds.resources if bed.patient}
        if not patients_by_id:
            return web_bed_group_schemas.WebBedGroupAlertResources.model_construct(resources=[])
        params = web_patient_schemas.WebGetPatientAlerts.model_construct(
            isAlert=True,
            patientIds=list(patients_by_id.keys()),
        )
        patient_observations = await self.patient_client.get_patients_observations(
            params.to_platform()
        )
        patient_observations_resources = (
            web_bed_group_schemas.WebBedGroupAlertResources.from_platform(
                patient_observations.resources, patients_by_id
            )
        )
        return patient_observations_resources
