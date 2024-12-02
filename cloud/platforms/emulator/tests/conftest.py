from unittest.mock import AsyncMock, patch

import pytest
import respx
from fastapi.testclient import TestClient

from src.emulator.memory_registry import DataManager
from src.emulator.task_proxy import TaskManager
from src.main import app
from tests.src.utils import MockEmulationManager, MockPublisher


@pytest.fixture
@respx.mock
def test_app():
    """Test app with mocked HTTPX requests"""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def mock_publisher():
    with patch("src.broker.KafkaClient", new_callable=AsyncMock) as mocked_kafka_client:
        mocked_publisher = MockPublisher()
        mocked_kafka_client.return_value = mocked_publisher
        yield mocked_publisher


@pytest.fixture(autouse=True)
def mock_start_emulation():
    with patch.object(
        target=TaskManager,
        attribute="start_emulation",
        new=MockEmulationManager.start_emulation,
    ):
        with patch.object(
            target=TaskManager,
            attribute="stop_emulation",
            new=MockEmulationManager.stop_emulation,
        ):
            yield MockEmulationManager
            MockEmulationManager._running_devices.clear()
            MockEmulationManager._emulations.clear()


@pytest.fixture(autouse=True)
def clean_memory_registry():
    data_manager = DataManager()
    yield
    data_manager.patient_monitors_registry.clear()
    data_manager.sensor_registry.clear()
    data_manager._instance = None
