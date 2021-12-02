from typing import Union

from django.contrib.messages.storage.base import Message as DjangoMessage, BaseStorage

from drf_messages import logger
from drf_messages.conf import messages_settings
from drf_messages.models import Message, MessageQuerySet


class DBStorage(BaseStorage):
    """
    Message storage backend to persistent messages storage in the database, with relation to the request's session.
    When no session is provided, fallbacks to a temporary storage in memory.
    """

    def __init__(self, request, *args, **kwargs):
        super(DBStorage, self).__init__(request, *args, **kwargs)
        # fallback to non-persistent message storage when no session is available
        if messages_settings.MESSAGES_USE_SESSIONS:
            self._fallback = not bool(hasattr(request, "session") and request.session.session_key)
        else:
            self._fallback = not bool(hasattr(request, "user") and request.user.is_authenticated)

    def get_queryset(self) -> MessageQuerySet:
        """
        Get queryset of all messages for that request session.
        :return: MessageQuerySet object
        """
        return Message.objects.with_context(self.request)

    def get_unread_queryset(self) -> MessageQuerySet:
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
                yield message.get_django_message()

            # update last read
            self.get_unread_queryset().mark_read()

    def __getitem__(self, key):
        if self._fallback:
            self.used = True
            return self._queued_messages[key]
        else:
            qs_slice = self.get_unread_queryset().prefetch_related("extra_tags")[key]
            if isinstance(qs_slice, Message):
                qs_slice.mark_read(self.request)
                return qs_slice.get_django_message()

            # update last read
            self.get_unread_queryset().filter(pk__in=qs_slice).mark_read()
            # parse to Django original Message objects
            return [
                message.get_django_message()
                for message in qs_slice
            ]

    def __contains__(self, item: Union[str, int, DjangoMessage]):
        if isinstance(item, str):
            if self._fallback:
                return any(item == m.message for m in self._queued_messages)
            else:
                return self.get_unread_queryset().filter(message=item).exists()
        elif isinstance(item, int):
            if self._fallback:
                return any(item == m.level for m in self._queued_messages)
            else:
                return self.get_unread_queryset().filter(level=item).exists()
        elif isinstance(item, DjangoMessage):
            if self._fallback:
                return item in self._queued_messages
            else:
                return self.get_unread_queryset().filter(message=item.message, level=item.level).exists()
        else:
            raise ValueError(f"Unsupported \"in\" condition with type {type(item)} in DBStorage")

    def __len__(self):
        if self._fallback:
            return len(self._queued_messages)
        else:
            return self.get_unread_queryset().count()

    def __bool__(self):
        if self._fallback:
            return bool(self._queued_messages)
        else:
            return self.get_unread_queryset().exists()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.get_queryset().mark_read()

    def _store(self, messages, response, *args, **kwargs):
        # messages are saved immediately when is created
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
        elif message and int(level) >= self.level:
            Message.objects.create_message(self.request, message, level, extra_tags=extra_tags)
        elif not message:
            logger.debug(f"Skip message creation due to an empty string. (message=\'{message}\')")
        elif level < self.level:
            logger.debug(f"Skip message creation due to the level being too low (level={level} / min={self.level}).")

    def update(self, response) -> None:
        # delete already read messages
        if messages_settings.MESSAGES_DELETE_READ and self.used and not self._fallback:
            count, _ = self.get_queryset().filter(read_at__isnull=False).delete()
            logger.info(f"Cleared {count} messages for session {self.request.session}")

    def __str__(self):
        results = self.__repr__()
        self.used = True
        if not self._fallback:
            self.get_unread_queryset().mark_read()
        return results

    def __repr__(self):
        if self._fallback:
            return ", ".join(m.message for m in self._queued_messages)
        else:
            return ", ".join(self.get_unread_queryset().values_list("message", flat=True))
