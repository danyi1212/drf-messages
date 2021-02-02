from django.contrib.messages.storage.base import LEVEL_TAGS
from rest_framework import serializers

from drf_messages.models import Message, MessageTag


class MessageSerializer(serializers.ModelSerializer):
    extra_tags = serializers.SlugRelatedField(slug_field="text", queryset=MessageTag.objects.all(), many=True)
    level = serializers.ChoiceField(choices=tuple(LEVEL_TAGS.items()))
    level_tag = serializers.ChoiceField(choices=tuple(LEVEL_TAGS.values()))

    class Meta:
        model = Message
        fields = ("id", "message", "level", "level_tag", "extra_tags", "view", "read_at", "created")
