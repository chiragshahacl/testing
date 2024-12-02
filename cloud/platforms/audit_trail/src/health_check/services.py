from src.health_check import schemas as health_schemas
from src.health_check.enums import HealthCheckStatus


class HealthCheckService:
    def okay(self) -> health_schemas.HealthCheck:
        response = health_schemas.HealthCheck(status=HealthCheckStatus.HEALTHY)
        return response
