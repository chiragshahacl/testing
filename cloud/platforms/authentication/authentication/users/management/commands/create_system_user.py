from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError  # type: ignore

from authentication.users.models import Privilege
from authentication.users.serializers import ManagementGetOrCreateUserSerializer


class Command(BaseCommand):
    help = "Creates a system user with defined list of parameters"

    def add_arguments(self, parser):
        parser.add_argument("--email", help="User's email (username)", type=str, required=True)
        parser.add_argument(
            "--groups", help="User's groups (comma-separated)", type=str, required=False
        )
        parser.add_argument("--password", help="User's password", type=str, required=True)
        parser.add_argument("--first_name", help="User's first name", type=str, required=True)
        parser.add_argument("--last_name", help="User's last name", type=str, required=True)

    def handle(self, *args, **kwargs):
        groups = kwargs.get("groups", "").split(",") if kwargs.get("groups") else []

        user_data = {
            "username": kwargs["email"],
            "email": kwargs["email"],
            "password": kwargs["password"],
            "first_name": kwargs["first_name"],
            "last_name": kwargs["last_name"],
        }

        privilege = []
        serializer = ManagementGetOrCreateUserSerializer(data=user_data)
        if not serializer.is_valid():
            for field_name, field_errors in serializer.errors.items():
                self.stderr.write(f"{field_name}:")
                for error in field_errors:
                    self.stderr.write(error)
            raise CommandError("Invalid parameter passed.")
        user = serializer.save()
        for group_name in groups:
            try:
                privilege.append(Privilege.objects.get(name=group_name))
            except ObjectDoesNotExist:
                self.stderr.write(f"Privilege '{group_name}' does not exist.")
                continue
        user.privileges.set(privilege)
