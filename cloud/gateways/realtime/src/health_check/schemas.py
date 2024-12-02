from pydantic import BaseModel

from src.health_check.enums import HealthCheckStatus


class HealthCheck(BaseModel):
    status: HealthCheckStatus
