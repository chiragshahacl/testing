import pytest

from src.cache import MetricsCacheService
from tests.factories.broker import BrokerMessageFactory, BrokerMessageHeadersFactory


class TestMetricsCacheService:
    @pytest.mark.asyncio
    async def test_cache(self):
        cache = MetricsCacheService()
        message_1 = BrokerMessageFactory.build(
            key="patient",
            headers=BrokerMessageHeadersFactory.build(
                code="1234",
                device_primary_identifier="device_id",
            ),
        )
        message_2 = BrokerMessageFactory.build(
            key="patient",
            headers=BrokerMessageHeadersFactory.build(
                code="4321",
                device_primary_identifier="device_id",
            ),
        )
        message_3 = BrokerMessageFactory.build(
            key="patient",
            value="override",
            headers=BrokerMessageHeadersFactory.build(
                code="1234",
                device_primary_identifier="device_id",
            ),
        )
        await cache.new_metrics_handler(message_1)
        await cache.new_metrics_handler(message_2)
        await cache.new_metrics_handler(message_3)

        result = cache.get_cached_metrics(message_1.key)
        assert set(result) == {message_2.value, message_3.value}
