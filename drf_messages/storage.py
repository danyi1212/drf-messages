from functools import lru_cache

from django.contrib.messages.storage.base import Message as DjangoMessage, BaseStorage

from drf_messages import logger
from drf_messages.conf import MESSAGES_DELETE_READ, MESSAGES_USE_SESSIONS
from drf_messages.models import Message


class DBStorage(BaseStorage):
    """
    Message storage backend to persistent messages storage in the database, with relation to the request's session.
    When no session is provided, it fallbacks to a temporary storage in memory.
    """

    def __init__(self, request, *args, **kwargs):
        super(DBStorage, self).__init__(request, *args, **kwargs)
        # fallback to non persistent message storage when no session is available
        if MESSAGES_USE_SESSIONS:
            self._fallback = not bool(hasattr(request, "session") and request.session.session_key)
        else:
            self._fallback = not bool(hasattr(request, "user") and request.user.is_authenticated)

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
        return self.get_queryset().filter(read_at__isnull=True)

    def __iter__(self):
        if self._fallback:
            self.used = True
            yield from self._queued_messages
        else:
            # parse to Django original Message objects
            for message in self.get_unread_queryset().prefetch_related("extra_tags"):
                yield DjangoMessage(
                    level=message.level,
                    message=message.message,
                    extra_tags=str(list(message.extra_tags.values_list("text", flat=True)))
                )

            # update last read
            self.get_queryset().mark_read()

    def __contains__(self, item: DjangoMessage):
        if self._fallback:
            return item in self._queued_messages
        else:
            return self.get_unread_queryset().filter(message=item.message, level=item.level).exists()

    @lru_cache()
    def __len__(self):
        if self._fallback:
            return len(self._queued_messages)
        else:
            return self.get_unread_queryset().count()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.get_queryset().mark_read()

    def _store(self, messages, response, *args, **kwargs):
        # messages are save on-demand when is created
        return []

    def _get(self, *args, **kwargs):
        if self._fallback:
            # avoid potential infinite loop, as the super method of __iter__ calls _get itself.
            return [], True
        else:
            return list(self.__iter__()), True

    def add(self, level: int, message: str, extra_tags=''):
        if self._fallback:
            # save messaged to temporary storage in memory
            self._queued_messages.append(DjangoMessage(level, message, extra_tags=extra_tags))
        else:
            if message and int(level) >= self.level:
                Message.objects.create_message(self.request, message, level, extra_tags=extra_tags)
            else:
                if not message:
                    logger.debug(f"Skip message creation due to an empty string. ({message})")
                elif level < self.level:
                    logger.debug(f"Skip message creation due to the level being too low ({level} / {self.level}.")

    def update(self, response):
        # delete already read messages
        if MESSAGES_DELETE_READ and self.used and not self._fallback:
            count, _ = self.get_queryset().filter(read_at__isnull=False).delete()
            logger.info(f"Cleared {count} messages for session {self.request.session}")

    def __str__(self):
        messages = [m.message for m in self.__iter__()]
        self.used = False
        return str(messages)

    def __repr__(self):
        return self.__str__()
