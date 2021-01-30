from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.models import Session

from drf_messages.models import Message, MessageTag


class DBStorage(FallbackStorage):
    did_read = False

    def _get(self, *args, **kwargs):
        # skip when is creating new messages
        if not self.added_new:
            # update seen_at for all messages
            Message.objects.with_context(self.request, update_seen=True)

        return super(DBStorage, self)._get(*args, **kwargs)

    def add(self, level: int, message: str, extra_tags=''):
        # only if there is an active session
        if self.request.session.session_key:
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

        return super(DBStorage, self).add(level, message, extra_tags=extra_tags)
