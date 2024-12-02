from uuid import UUID

import pytest

from src.bed_group.schemas import (
    WebBatchCreateOrUpdateBedGroup,
    WebCreateOrUpdateBedGroup,
)
from src.bed_group.services import BedGroupService


@pytest.mark.asyncio
async def test_batch_create_or_update_bed_groups(mocker):
    existing_bed_groups = mocker.MagicMock(
        resources=[
            WebCreateOrUpdateBedGroup(
                id=UUID("28454f31-1c66-428a-b0a0-0d973f8b1f00"), name="Bed Group 1"
            ),
            WebCreateOrUpdateBedGroup(
                id=UUID("eb00148f-86fb-478b-877a-18fb554b72c6"), name="Bed Group 2"
            ),
            WebCreateOrUpdateBedGroup(
                id=UUID("d7f134c6-231d-4b96-bcf1-285e48b3e3ef"), name="Bed Group 3"
            ),
        ]
    )
    payload_beds = mocker.MagicMock(
        resources=[
            WebCreateOrUpdateBedGroup(id=None, name="Bed Group 4"),
            WebCreateOrUpdateBedGroup(id=existing_bed_groups.resources[0].id, name="Bed Group 5"),
            WebCreateOrUpdateBedGroup(id=None, name="Bed Group 6"),
            WebCreateOrUpdateBedGroup(id=existing_bed_groups.resources[1].id, name="Bed Group 7"),
            WebCreateOrUpdateBedGroup(id=existing_bed_groups.resources[2].id, name="Bed Group 3"),
        ]
    )
    bed_groups_to_create = [bed for bed in payload_beds.resources if not bed.id]
    bed_groups_to_update = [payload_beds.resources[1], payload_beds.resources[3]]

    patient_client_class_mock = mocker.patch("src.bed_group.services.PatientPlatformClient")
    patient_client_mock = patient_client_class_mock.return_value
    patient_client_mock.get_bed_groups = mocker.AsyncMock(return_value=existing_bed_groups)
    patient_client_mock.update_bed_group_batch = mocker.AsyncMock()
    patient_client_mock.create_bed_group_batch = mocker.AsyncMock()
    to_platform_batch_create_mock = mocker.patch.object(
        WebBatchCreateOrUpdateBedGroup, "to_platform_batch_create"
    )
    to_platform_batch_update_mock = mocker.patch.object(
        WebBatchCreateOrUpdateBedGroup, "to_platform_batch_update"
    )

    await BedGroupService().batch_create_or_update_bed_groups(payload_beds)

    patient_client_mock.get_bed_groups.assert_called_once_with()
    to_platform_batch_update_mock.assert_called_once_with(bed_groups_to_update)
    patient_client_mock.update_bed_group_batch.assert_called_once_with(
        to_platform_batch_update_mock.return_value
    )
    to_platform_batch_create_mock.assert_called_once_with(bed_groups_to_create)
    patient_client_mock.create_bed_group_batch.assert_called_once_with(
        to_platform_batch_create_mock.return_value
    )
