from django.conf import settings


# Allow the deletion of unread messages through DRF view
MESSAGES_ALLOW_DELETE_UNREAD: bool = getattr(settings, "MESSAGES_ALLOW_DELETE_UNREAD", False)
# Automatically read all seen messages after request
MESSAGES_DELETE_SEEN: bool = getattr(settings, "MESSAGES_DELETE_SEEN", False)
