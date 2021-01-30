from django.conf import settings


# Message "message" field max length (require migration after change)
MESSAGES_MAX_LENGTH: bool = getattr(settings, "MESSAGES_MAX_LENGTH", 2048)
# Message "view" field max length (require migration after change)
MESSAGES_VIEW_MAX_LENGTH: bool = getattr(settings, "MESSAGES_VIEW_MAX_LENGTH", 128)
# MessageTag "text" field max length (require migration after change)
MESSAGES_TAG_MAX_LENGTH: bool = getattr(settings, "MESSAGES_TAG_MAX_LENGTH", 2048)


