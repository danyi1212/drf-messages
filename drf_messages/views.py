# pylint: disable=import-outside-toplevel, inconsistent-return-statements, no-member
from django.contrib.messages import get_messages
from django.contrib.messages.storage.base import LEVEL_TAGS
from django.db.models import Count, Max
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from drf_messages.conf import messages_settings
from drf_messages.serializers import MessageSerializer, MessagePeekSerializer
from drf_messages.storage import DBStorage


def get_filter_class():
    """Load filter class if is able to import django_filters"""
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
        """
        Get queryset for all relevant messages
        :return: QuerySet for drf_messages.Message
        :exception ValueError: Messages storage is not configured properly.
        """
        messages: DBStorage = get_messages(self.request)
        if not isinstance(messages, DBStorage):
            raise ValueError("\"drf_messages\" is not installed properly. "
                             "Make sure MESSAGE_STORAGE is set to \"drf_messages.storage.DBStorage\"")

        return messages.get_queryset()

    def check_object_permissions(self, request, obj):
        super(MessagesViewSet, self).check_object_permissions(request, obj)
        # restrict deletion of unread messages.
        if not messages_settings.MESSAGES_ALLOW_DELETE_UNREAD and self.action == "destroy" and obj.read_at is None:
            raise PermissionDenied("You do not have the permission to delete unread messages")

    def list(self, request, *args, **kwargs):
        response = super(MessagesViewSet, self).list(request, *args, **kwargs)
        # update read at
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            queryset.filter(pk__in=map(lambda x: x.pk, page)).mark_read()
        else:
            queryset.mark_read()
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super(MessagesViewSet, self).retrieve(request, *args, **kwargs)
        # update read at
        self.get_object().mark_read(self.request)
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
        return Response(serializer.data, status.HTTP_200_OK)
