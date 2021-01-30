from django.contrib.messages.storage.base import LEVEL_TAGS
from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from drf_messages.conf import MESSAGES_MAX_LENGTH, MESSAGES_VIEW_MAX_LENGTH, MESSAGES_TAG_MAX_LENGTH


class MessageManager(models.Manager):

    def with_context(self, request, update_seen=True):
        """
        Filter only messages related for a request session.
        """
        queryset = self.get_queryset().filter(session__session_key=request.session.session_key)
        if update_seen:
            queryset.update(seen_at=timezone.now())
            # Mark that messages have been read
            request._messages.did_read = True

        return queryset


class MessageTag(models.Model):
    message = models.ForeignKey("drf_messages.Message", on_delete=models.CASCADE, related_name="extra_tags")

    text = models.CharField(max_length=MESSAGES_TAG_MAX_LENGTH, help_text="Custom tags for the message.")

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text


class Message(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="messages",
                                help_text="The session where the message was submitted to.")
    view = models.CharField(max_length=MESSAGES_VIEW_MAX_LENGTH, blank=True,
                            help_text="The view where the message was submitted from.")

    message = models.CharField(max_length=MESSAGES_MAX_LENGTH, blank=True, help_text="The actual text of the message.")
    level = models.IntegerField(help_text="An integer describing the type of the message.")

    seen_at = models.DateTimeField(blank=True, null=True, default=None, help_text="When the message was seen.")

    created = models.DateTimeField(auto_now_add=True)

    objects = MessageManager()

    class Meta:
        ordering = ["-created"]

    @cached_property
    def level_tag(self):
        return LEVEL_TAGS.get(self.level, '')

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message
