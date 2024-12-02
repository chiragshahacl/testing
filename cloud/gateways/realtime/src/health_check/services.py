from src.health_check.enums import HealthCheckStatus
from src.health_check.schemas import HealthCheck


class HealthCheckService:
    def okay(self) -> HealthCheck:
        return HealthCheck(status=HealthCheckStatus.HEALTHY)
