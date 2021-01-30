from django.contrib.messages.storage.base import LEVEL_TAGS
from django.contrib.sessions.models import Session
from django.db import models
from django.utils.functional import cached_property


# TODO move to settings
MESSAGES_MAX_LENGTH = 2048
MESSAGES_TAG_MAX_LENGTH = 2048


class MessageQuerySet(models.QuerySet):

    def with_context(self, request):
        """
        Filter only messages related for a request session.
        """
        return self.filter(session__session_key=request.session.session_key)


class MessageManager(models.Manager):

    def get_queryset(self):
        return MessageQuerySet(self.model, using=self._db)

    def with_context(self, request):
        """
        Filter only messages related for a request session.
        """
        return self.get_queryset().with_context(request)


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
    view = models.CharField(max_length=128, blank=True, help_text="The view where the message was submitted from.")

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
