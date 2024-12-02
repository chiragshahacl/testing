from app.health_check.enums import HealthCheckStatus


def test_health_check_statuses():
    assert HealthCheckStatus.HEALTHY.value == "Healthy"
    assert HealthCheckStatus.ERROR.value == "Error"
