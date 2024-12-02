from django.contrib.auth import get_user_model  # type: ignore
from django.core.management import call_command  # type: ignore
from django.test import TestCase  # type: ignore

from authentication.users.models import Privilege

User = get_user_model()


class CreateSystemUserCommandTest(TestCase):
    def setUp(self):
        # Set up initial data for the test
        self.email = "testuser@example.com"
        self.password = "password123"
        self.first_name = "Test"
        self.last_name = "User"
        self.groups = ["clinical", "tech", "organization"]

        # Create groups
        for group_name in self.groups:
            Privilege.objects.get_or_create(name=group_name)

    def test_create_system_user(self):
        # Call the command
        call_command(
            "create_system_user",
            email=self.email,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
            groups=",".join(self.groups),
        )

        # Fetch the user
        user = User.objects.get(email=self.email)

        # Check user attributes
        self.assertEqual(user.username, self.email)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.last_name, self.last_name)
        self.assertTrue(user.check_password(self.password))

    def test_create_system_user_invalid_data(self):
        # Call the command with missing email
        with self.assertRaises(TypeError) as response:
            call_command(
                "create_system_user",
                email="",  # Invalid email
                password=self.password,
                first_name=self.first_name,
                last_name=self.last_name,
                groups=",".join(self.groups),
                verbosity=0,
                interactive=False,
            )
        self.assertIn(
            "Unknown option(s) for create_system_user command: interactive. Valid options are:",
            str(response.exception),
        )
