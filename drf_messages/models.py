from django.contrib.messages import get_messages
from django.contrib.messages.storage.base import LEVEL_TAGS
from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from drf_messages import logger


class MessageQuerySet(models.QuerySet):

    def __init__(self, model=None, query=None, using=None, hints=None, request_context=None):
        super(MessageQuerySet, self).__init__(model=model, query=query, using=using, hints=hints)
        self.request_context = request_context

    def _clone(self):
        # pass request context on clone
        c = super(MessageQuerySet, self)._clone()
        c.request_context = self.request_context
        return c

    def mark_read(self):
        """
        Mark any unread messages as read now.
        :return: Number of messages updated
        """
        # mark that messages have been read from the request
        result = self.filter(read_at__isnull=True).update(read_at=timezone.now())
        logger.debug(f"Marked {result} messages as read for session {self.request_context.session.session_key}")
        if result > 0 and self.request_context:
            storage = get_messages(self.request_context)
            if storage is not None:
                storage.used = True
            else:
                logger.warning("Message storage is None. Make sure to include "
                               "\"'django.contrib.messages.middleware.MessageMiddleware'\" in the MIDDLEWARE setting.")
        return result


class MessageManager(models.Manager):

    def with_context(self, request):
        """
        Filter only messages related for a request session.
        """
        return MessageQuerySet(self.model, using=self._db, request_context=request).filter(
            session__session_key=request.session.session_key)


class MessageTag(models.Model):
    message = models.ForeignKey("drf_messages.Message", on_delete=models.CASCADE, related_name="extra_tags")

    text = models.CharField(max_length=128, help_text="Custom tags for the message.")

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text


class Message(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="messages",
                                help_text="The session where the message was submitted to.")
    view = models.CharField(max_length=64, blank=True,
                            help_text="The view where the message was submitted from.")

    message = models.CharField(max_length=1024, blank=True, help_text="The actual text of the message.")
    level = models.IntegerField(help_text="An integer describing the type of the message.")

    read_at = models.DateTimeField(blank=True, null=True, default=None, help_text="When the message was read.")

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
