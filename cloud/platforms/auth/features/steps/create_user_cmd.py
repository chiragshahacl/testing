from behave import *
from sqlalchemy import select

from app.auth import crypto
from app.auth.models import Role, User


def get_db_roles(context) -> dict[str, Role]:
    stmt = select(Role)
    result = context.db.execute(stmt)
    return {r.name: r for r in result.scalars().all()}


@when("the request to create an user is made")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("a request to create an user with roles `{roles}`")
def step_impl(context, roles: str):
    db_roles = get_db_roles(context)

    request_roles = []
    for r in roles.split(","):
        role_name = r.strip().lower()
        db_role = db_roles[role_name]
        request_roles.append(
            {
                "id": str(db_role.id),
            }
        )

    context.request = {"url": "/auth/CreateUser", "json": {"roles": request_roles}}


@step("the user will have username `{username}`")
def step_impl(context, username: str):
    context.request["json"]["username"] = username


@step("the user will have password `{password}`")
def step_impl(context, password: str):
    context.request["json"]["password"] = password


@step("the user is created")
def step_impl(context):
    username = context.request["json"]["username"]
    stmt = select(User).where(User.username == username.lower())
    found_user = context.db.execute(stmt).scalars().unique().one_or_none()
    assert found_user is not None
    assert found_user.password != context.request["json"]["password"]
    assert found_user.username == context.request["json"]["username"]
    assert {str(r.id) for r in found_user.roles} == {
        r["id"] for r in context.request["json"]["roles"]
    }

    match, _ = crypto.verify_password(context.request["json"]["password"], found_user.password)
    assert match


@step("the user is not created")
def step_impl(context):
    username = context.request["json"]["username"]
    stmt = select(User).where(User.username == username.lower())
    found_user = context.db.execute(stmt).scalars().unique().one_or_none()
    assert found_user is None
