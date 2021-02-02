from django.contrib.messages.storage.base import LEVEL_TAGS
from django_filters import FilterSet, BooleanFilter, TypedChoiceFilter, CharFilter, DateTimeFromToRangeFilter

from drf_messages.models import Message

REVERSED_LEVEL_TAGS = {
    v: k for k, v in LEVEL_TAGS.items()
}


class MessageFilterSet(FilterSet):
    unread = BooleanFilter(field_name="read_at", lookup_expr="isnull", label="unread")
    extra_tags = CharFilter(field_name="extra_tags__text")
    level_tag = TypedChoiceFilter(choices=zip(LEVEL_TAGS.values(), LEVEL_TAGS.values()), lookup_expr="gte",
                                  field_name="level", label="level_tag", coerce=lambda k: REVERSED_LEVEL_TAGS.get(k))
    read = DateTimeFromToRangeFilter(field_name="read_at", label="read")
    created = DateTimeFromToRangeFilter()

    class Meta:
        model = Message
        fields = ("unread", "level_tag", "level", "extra_tags", "view", "read", "created")
