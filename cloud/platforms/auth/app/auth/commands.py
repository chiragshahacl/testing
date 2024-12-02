from fastapi import APIRouter, Depends

from app.auth.crypto import JWTClaims
from app.auth.enums import RoleNames
from app.auth.schemas import CreateUserSchema
from app.auth.services import UserService
from app.common.dependencies import UserHasRole
from app.settings import config

api = APIRouter(prefix=config.BASE_PATH)


@api.post("/CreateUser")
async def create_user_command(
    payload: CreateUserSchema,
    service: UserService = Depends(),
    claims: JWTClaims = Depends(UserHasRole({RoleNames.ADMIN})),
):
    user = await service.create_user(claims, payload)
    return user
