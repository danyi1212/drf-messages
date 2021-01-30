from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from drf_messages.conf import MESSAGES_DELETE_UNREAD
from drf_messages.models import Message
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
        # update seen_at only when listing
        return Message.objects.with_context(self.request, update_seen=self.action == "list")

    def check_object_permissions(self, request, obj):
        super(MessagesViewSet, self).check_object_permissions(request, obj)
        # restrict deletion of unread messages.
        if not MESSAGES_DELETE_UNREAD and self.action == "destroy" and obj.seen_at is None:
            raise PermissionDenied("Unread messages cannot be deleted.")
