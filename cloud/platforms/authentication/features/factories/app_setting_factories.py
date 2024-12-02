import factory
from authentication.config.models import AppSetting


class AppSettingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AppSetting
        django_get_or_create = ("key",)

    key = factory.Faker("word")
    value = factory.Faker("word")
