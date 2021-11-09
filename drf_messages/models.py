from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.messages.storage.base import LEVEL_TAGS
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import cached_property

from drf_messages import logger
from drf_messages.conf import messages_settings


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
        Filter only messages for a request context:
        When MESSAGES_USE_SESSIONS, messages for that session or without a session specified,
        otherwise messages from all sessions.
        """
        queryset = MessageQuerySet(self.model, using=self._db, request_context=request).filter(
            user=request.user if hasattr(request, "user") and request.user.is_authenticated else None
        )
        if messages_settings.MESSAGES_USE_SESSIONS:
            return queryset.filter(Q(session__session_key=request.session.session_key) | Q(session__isnull=True))
        else:
            return queryset

    def _create_extra_tags(self, message, extra_tags):
        """
        Create message tags from list or string.
        :param message: The message to attach the tags to.
        :param extra_tags: String or List of string tags.
        :return: None
        """
        if isinstance(extra_tags, (list, tuple, set)):
            MessageTag.objects.bulk_create((
                MessageTag(message=message, text=tag)
                for tag in extra_tags
            ))
        else:
            MessageTag.objects.create(message=message, text=str(extra_tags))

    def create_message(self, request, message, level, extra_tags=None):
        """
        Create a new message to the database.
        :param request: Request context.
        :param message: Text body of the message.
        :param level: Integer describing the type of the message.
        :param extra_tags: One or more tags to attach to the message.
        :return: Message object.
        """
        # extract session
        if hasattr(request, "session") and request.session.session_key:
            session = Session.objects.get(session_key=request.session.session_key)
        else:
            session = None
        # create message
        message_obj = self.create(
            user=request.user,
            session=session,
            view=request.resolver_match.view_name if request.resolver_match else '',
            message=message,
            level=level,
        )
        # create extra tags
        if extra_tags:
            self._create_extra_tags(message_obj, extra_tags)

        return message_obj

    def create_user_message(self, user, message, level, extra_tags=None):
        """
        Create a new message to the database.
        :param user: User object (from settings.AUTH_USER_MODEL).
        :param message: Text body of the message.
        :param level: Integer describing the type of the message.
        :param extra_tags: One or more tags to attach to the message.
        :return: Message object.
        """
        # create message
        message_obj = self.create(
            user=user,
            message=message,
            level=level,
        )
        # create extra tags
        if extra_tags:
            self._create_extra_tags(message_obj, extra_tags)

        return message_obj


class MessageTag(models.Model):
    message = models.ForeignKey("drf_messages.Message", on_delete=models.CASCADE, related_name="extra_tags")

    text = models.CharField(max_length=128, help_text="Custom tags for the message.")

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text


class Message(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="messages")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True, default=None,
                                related_name="messages", help_text="The session where the message was submitted to.")
    view = models.CharField(max_length=64, blank=True, default="",
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
