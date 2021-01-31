from django.contrib.messages.storage.base import BaseStorage
from django.contrib.sessions.models import Session
from django.contrib.messages.storage.base import Message as DjangoMessage

from drf_messages import logger
from drf_messages.conf import MESSAGES_DELETE_SEEN
from drf_messages.models import Message, MessageTag


class DBStorage(BaseStorage):

    def get_queryset(self):
        """
        Get queryset of all messages for that request session.
        :return: MessageQuerySet object
        """
        return Message.objects.with_context(self.request)

    def get_unread_queryset(self):
        """
        Get queryset of unread messages for that request session.
        :return: MessageQuerySet object
        """
        return self.get_queryset().filter(seen_at__isnull=True)

    def __iter__(self):
        # parse to Django original Message objects
        for message in self.get_unread_queryset():
            yield DjangoMessage(
                level=message.level,
                message=message.message,
                extra_tags=str(list(message.extra_tags.values_list("text", flat=True)))
            )

        # update last seen
        self.get_queryset().mark_seen()

    def __contains__(self, item: DjangoMessage):
        return self.get_unread_queryset().filter(message=item.message, level=item.level).exists()

    def __len__(self):
        return self.get_unread_queryset().count()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.get_queryset().mark_seen()

    def _store(self, messages, response, *args, **kwargs):
        # messages are save on-demand when is created
        return []

    def _get(self, *args, **kwargs):
        return list(self.__iter__()), True

    def add(self, level: int, message: str, extra_tags=''):
        # only if there is an active session
        if message and int(level) >= self.level and self.request.session.session_key:
            self.added_new = True
            message_obj = Message.objects.create(
                session=Session.objects.get(session_key=self.request.session.session_key),
                view=self.request.resolver_match.view_name,
                message=message,
                level=level,
            )
            # create extra tags
            if isinstance(extra_tags, (list, tuple, set)):
                MessageTag.objects.bulk_create((
                    MessageTag(message=message_obj, text=tag)
                    for tag in extra_tags
                ))
            elif extra_tags:
                MessageTag.objects.create(message=message_obj, text=str(extra_tags))
        else:
            if not message:
                logger.debug(f"Skip message creation due to an empty string. ({message})")
            elif level < self.level:
                logger.debug(f"Skip message creation due to the level being too low ({level} / {self.level}.")
            else:
                logger.warning(f"Unable to create a message from view \"{self.request.resolver_match.view_name}\" "
                               f"because there no session in the request.")

    def update(self, response):
        # delete already seen messages
        if MESSAGES_DELETE_SEEN and self.used:
            count, _ = self.get_queryset().filter(seen_at__isnull=False).delete()
            logger.info(f"Cleared {count} messages for session {self.request.session}")
