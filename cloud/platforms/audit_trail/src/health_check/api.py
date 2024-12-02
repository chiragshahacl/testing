from fastapi import APIRouter, Depends

from src.health_check.schemas import HealthCheck
from src.health_check.services import HealthCheckService

api = APIRouter()


@api.get("/health")
async def get_health_check_api(
    health_check_service: HealthCheckService = Depends(),
) -> HealthCheck:
    return health_check_service.okay()
