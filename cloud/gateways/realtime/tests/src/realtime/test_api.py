from uuid import UUID

import pytest

from src.common.clients.patient.schemas import BedResourcesSchema
from src.common.clients.patient.services import PatientService
from src.realtime.api import vitals_consumer
from tests.factories.patient import BedFactory, PatientFactory


@pytest.mark.asyncio
async def test_vitals_consumer(mocker):
    bed_resources = BedResourcesSchema.model_construct(
        resources=[
            BedFactory.build(patient=None),
            BedFactory.build(patient=PatientFactory.build()),
        ]
    )
    mocker.patch.object(PatientService, "get_beds", return_value=bed_resources)
    ws = mocker.Mock(accept=mocker.AsyncMock(), send_text=mocker.AsyncMock())
    ws.iter_json.return_value = mocker.AsyncMock()
    token = "1234"

    await vitals_consumer(ws, token)
