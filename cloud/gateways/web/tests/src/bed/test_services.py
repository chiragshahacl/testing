from uuid import UUID

import pytest

from src.bed.schemas import WebBatchCreateOrUpdateBeds, WebUpdateOrCreateBed
from src.bed.services import BedService


@pytest.mark.asyncio
async def test_create_update_logic(mocker):
    existing_beds = mocker.MagicMock(
        resources=[
            WebUpdateOrCreateBed(id=UUID("28454f31-1c66-428a-b0a0-0d973f8b1f00"), name="Bed 1"),
            WebUpdateOrCreateBed(id=UUID("eb00148f-86fb-478b-877a-18fb554b72c6"), name="Bed 2"),
            WebUpdateOrCreateBed(id=UUID("d7f134c6-231d-4b96-bcf1-285e48b3e3ef"), name="Bed 3"),
        ]
    )
    payload_beds = mocker.MagicMock(
        resources=[
            WebUpdateOrCreateBed(id=None, name="Bed 4"),
            WebUpdateOrCreateBed(id=existing_beds.resources[0].id, name="Bed 5"),
            WebUpdateOrCreateBed(id=None, name="Bed 6"),
            WebUpdateOrCreateBed(id=existing_beds.resources[1].id, name="Bed 7"),
            WebUpdateOrCreateBed(id=existing_beds.resources[2].id, name="Bed 3"),
        ]
    )
    beds_to_create = [bed for bed in payload_beds.resources if not bed.id]
    beds_to_update = [payload_beds.resources[1], payload_beds.resources[3]]

    patient_client_class_mock = mocker.patch("src.bed.services.PatientPlatformClient")
    patient_client_mock = patient_client_class_mock.return_value
    patient_client_mock.get_beds = mocker.AsyncMock(return_value=existing_beds)
    patient_client_mock.update_bed_batch = mocker.AsyncMock()
    patient_client_mock.create_bed_batch = mocker.AsyncMock()
    to_platform_batch_create_mock = mocker.patch.object(
        WebBatchCreateOrUpdateBeds, "to_platform_batch_create"
    )
    to_platform_batch_update_mock = mocker.patch.object(
        WebBatchCreateOrUpdateBeds, "to_platform_batch_update"
    )

    await BedService().create_or_update_beds(payload_beds)

    patient_client_mock.get_beds.assert_called_once_with()
    to_platform_batch_update_mock.assert_called_once_with(beds_to_update)
    patient_client_mock.update_bed_batch.assert_called_once_with(
        to_platform_batch_update_mock.return_value
    )
    to_platform_batch_create_mock.assert_called_once_with(beds_to_create)
    patient_client_mock.create_bed_batch.assert_called_once_with(
        to_platform_batch_create_mock.return_value
    )
