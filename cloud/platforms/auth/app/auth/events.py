import uuid
from typing import Optional

from app.auth import crypto
from app.auth.models import Role, User
from app.auth.schemas import SecretPassword
from app.common.event_sourcing.events import Event


class CreateUserEvent(Event[User]):
    event_type: str = "USER_CREATE_EVENT"
    display_name: str = "User created"

    def __init__(self, requester_username: str, username: str, password: SecretPassword):
        super().__init__(requester_username)
        self.username = username
        self.password = password

    def process(self, entity: Optional[User] = None) -> User:
        return User(
            id=uuid.uuid4(),
            username=self.username.lower(),
            password=crypto.hash_password(self.password.get_secret_value()),
        )


class AddRoleToUserEvent(Event[User]):
    event_type: str = "USER_ADD_ROLE_EVENT"
    display_name: str = "Role added to user"

    def __init__(self, requester_username: str, role: Role):
        super().__init__(requester_username)
        self.role = role

    def process(self, entity: User) -> User:
        entity.roles.append(self.role)
        return entity
