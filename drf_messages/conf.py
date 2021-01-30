from django.conf import settings


# Allow the deletion of unread messages through DRF view
MESSAGES_DELETE_UNREAD: bool = getattr(settings, "MESSAGES_DELETE_UNREAD", False)
