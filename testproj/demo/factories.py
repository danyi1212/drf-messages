from django.contrib.messages.storage.base import LEVEL_TAGS
from factory import SubFactory, Faker, RelatedFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from demo.user_factories import UserFactory
from drf_messages.models import Message, MessageTag


class MessageTagFactory(DjangoModelFactory):
    text = Faker("word")
    message = SubFactory("demo.factories.MessageFactory")

    class Meta:
        model = MessageTag


class MessageFactory(DjangoModelFactory):
    message = Faker("text")
    user = SubFactory(UserFactory)
    view = ''
    level = FuzzyChoice(LEVEL_TAGS)
    extra_tags = RelatedFactory(MessageTagFactory, factory_related_name="message")

    class Meta:
        model = Message
