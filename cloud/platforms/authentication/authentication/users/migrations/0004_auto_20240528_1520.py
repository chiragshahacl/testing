from django.conf import settings
from django.db import migrations


def update_user_privileges(apps, schema_editor):
    User = apps.get_model("users", "User")
    Privilege = apps.get_model("users", "Privilege")

    clinical_privilege, _ = Privilege.objects.get_or_create(name=settings.CLINICAL_PRIVILEGE_NAME)
    tech_privilege, _ = Privilege.objects.get_or_create(name=settings.TECH_PRIVILEGE_NAME)
    organization_privilege, _ = Privilege.objects.get_or_create(
        name=settings.ORGANIZATION_PRIVILEGE_NAME
    )

    # Update existing users' privileges
    for user in User.objects.all():
        user.privileges.set([clinical_privilege])


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_user_blocked_until"),
    ]

    operations = [
        migrations.RunPython(update_user_privileges),
    ]
