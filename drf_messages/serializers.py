from django.contrib.messages.storage.base import LEVEL_TAGS
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from drf_messages.models import Message, MessageTag


class MessageSerializer(serializers.ModelSerializer):
    extra_tags = serializers.SlugRelatedField(slug_field="text", queryset=MessageTag.objects.all(), many=True)
    level = serializers.ChoiceField(choices=tuple(LEVEL_TAGS.items()))
    level_tag = serializers.ChoiceField(choices=tuple(LEVEL_TAGS.values()))

    class Meta:
        model = Message
        fields = ("id", "message", "level", "level_tag", "extra_tags", "view", "read_at", "created")


class MessagePeekSerializer(serializers.Serializer):
    count = serializers.IntegerField(read_only=True, help_text="Count of unread messages.")
    max_level = serializers.ChoiceField(read_only=True, choices=tuple(LEVEL_TAGS.items()),
                                        help_text="Highest unread message level.")
    max_level_tag = serializers.ChoiceField(read_only=True, choices=tuple(LEVEL_TAGS.values()), allow_blank=True,
                                            help_text="Highest unread message level tag.")

    def update(self, instance, validated_data):
        raise ValidationError("Updating MessagePeek objects is not allowed.")

    def create(self, validated_data):
        raise ValidationError("Creating MessagePeek objects is not allowed.")
