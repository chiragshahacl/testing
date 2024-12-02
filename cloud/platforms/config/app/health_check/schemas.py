from pydantic import BaseModel

from app.health_check.enums import HealthCheckStatus


class HealthCheck(BaseModel):
    status: HealthCheckStatus
