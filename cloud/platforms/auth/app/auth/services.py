from fastapi.params import Depends

from app.auth.crypto import JWTClaims
from app.auth.events import AddRoleToUserEvent, CreateUserEvent
from app.auth.models import Role
from app.auth.repository import UserRepository
from app.auth.schemas import CreateUserSchema, UserSchema
from app.auth.stream import UserEventStream


class UserService:
    def __init__(
        self,
        read_user_repository: UserRepository = Depends(),
        user_event_stream: UserEventStream = Depends(),
    ):
        self.read_user_repository = read_user_repository
        self.user_event_stream = user_event_stream

    async def _get_roles_by_id(self) -> list[Role]:
        roles = await self.read_user_repository.get_roles()
        return {r.id: r for r in roles}

    async def create_user(self, claims: JWTClaims, payload: CreateUserSchema) -> UserSchema:
        roles_by_id = await self._get_roles_by_id()
        events = [CreateUserEvent(claims.username, payload.username, payload.password)]

        for role in payload.roles:
            found_role = roles_by_id[role.id]
            events.append(AddRoleToUserEvent(claims.username, found_role))

        user = None
        for event in events:
            user = await self.user_event_stream.add(event, user)
        return UserSchema.model_validate(user)
