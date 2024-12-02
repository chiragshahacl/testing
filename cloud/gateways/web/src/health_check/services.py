from src.health_check.enums import HealthCheckStatus
from src.health_check.schemas import HealthCheck


class HealthCheckService:
    def okay(self) -> HealthCheck:
        response = HealthCheck(status=HealthCheckStatus.HEALTHY)
        return response
