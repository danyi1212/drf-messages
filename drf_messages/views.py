from django.contrib.messages import get_messages
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from drf_messages.conf import MESSAGES_ALLOW_DELETE_UNREAD
from drf_messages.serializers import MessageSerializer


class MessagesViewSet(viewsets.mixins.ListModelMixin,
                      viewsets.mixins.RetrieveModelMixin,
                      viewsets.mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    List, Retrieve and Delete messages for this session.
    """
    serializer_class = MessageSerializer

    def get_queryset(self):
        return get_messages(self.request).get_queryset()

    def check_object_permissions(self, request, obj):
        super(MessagesViewSet, self).check_object_permissions(request, obj)
        # restrict deletion of unread messages.
        if not MESSAGES_ALLOW_DELETE_UNREAD and self.action == "destroy" and obj.seen_at is None:
            raise PermissionDenied("Unread messages cannot be deleted.")

    def list(self, request, *args, **kwargs):
        response = super(MessagesViewSet, self).list(request, *args, **kwargs)
        # update last seen
        self.get_queryset().mark_seen()
        return response
