import coreapi
import coreschema
from django.contrib.messages import get_messages
from django.contrib.messages.storage.base import LEVEL_TAGS
from django.db.models import Count, Max
from rest_framework import viewsets
from rest_framework.decorators import action, schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema

from drf_messages.conf import MESSAGES_ALLOW_DELETE_UNREAD
from drf_messages.serializers import MessageSerializer, MessagePeekSerializer


def get_filter_class():
    try:
        from drf_messages.filters import MessageFilterSet
        return MessageFilterSet
    except ImportError:
        return


class MessagesViewSet(viewsets.mixins.ListModelMixin,
                      viewsets.mixins.RetrieveModelMixin,
                      viewsets.mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    List, Retrieve and Delete messages for this session.
    """
    serializer_class = MessageSerializer
    search_fields = ("message",)
    ordering_fields = ("level", "read_at", "created")
    filterset_class = get_filter_class()

    def get_queryset(self):
        return get_messages(self.request).get_queryset()

    def check_object_permissions(self, request, obj):
        super(MessagesViewSet, self).check_object_permissions(request, obj)
        # restrict deletion of unread messages.
        if not MESSAGES_ALLOW_DELETE_UNREAD and self.action == "destroy" and obj.read_at is None:
            raise PermissionDenied("Unread messages cannot be deleted.")

    def list(self, request, *args, **kwargs):
        response = super(MessagesViewSet, self).list(request, *args, **kwargs)
        # update last read
        self.get_queryset().mark_read()
        return response

    @action(methods=["GET"], detail=False, description="Get unread messages count and level without reading them.",
            serializer_class=MessagePeekSerializer, pagination_class=None, filterset_class=None)
    def peek(self, request):
        """
        Get summary about unread message without reading them.
        """
        summary = self.get_queryset().filter(read_at__isnull=True).aggregate(
            count=Count("id"),
            max_level=Max("level"),
        )
        serializer = MessagePeekSerializer({
            **summary,
            "max_level_tag": LEVEL_TAGS.get(summary.get("max_level"), '')
        })
        return Response(serializer.data, 200)
