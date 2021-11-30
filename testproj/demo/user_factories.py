from django.contrib.auth import get_user_model
from factory import Faker, Sequence, LazyAttribute
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    username = Sequence(lambda i: f"test-user-{i}")
    email = LazyAttribute(lambda obj: f"{obj.username}@{Faker('domain_name')}")
    is_active = True
    is_staff = False
    is_superuser = False
    password = None

    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)  # Just user the create_user method recommended by Django


class AdminFactory(UserFactory):
    is_staff = True
    is_superuser = True
