from fastapi import APIRouter, Depends
from sentry_sdk import configure_scope

from src.health_check.schemas import HealthCheck
from src.health_check.services import HealthCheckService

api = APIRouter()


@api.get("/health")
def get_health_check_api(
    health_check_service: HealthCheckService = Depends(),
) -> HealthCheck:
    with configure_scope() as scope:
        if scope.transaction:
            scope.transaction.sampled = False
    return health_check_service.okay()
