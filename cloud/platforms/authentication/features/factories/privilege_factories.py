import factory
from authentication.users.models import Privilege


class PrivilegeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Privilege
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: "group%d" % n)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of users were passed in, use them
            for user in extracted:
                self.members.add(user)
