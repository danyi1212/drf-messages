from dataclasses import dataclass, fields

from django.conf import settings
from django.core.signals import setting_changed
from django.dispatch import receiver


@dataclass()
class DrfMessagesSettings:
    # Allow the deletion of unread messages through DRF view
    MESSAGES_ALLOW_DELETE_UNREAD: bool = False
    # Automatically read all read messages after request
    MESSAGES_DELETE_READ: bool = False
    # Use request session for storing messages
    MESSAGES_USE_SESSIONS: bool = False

    @classmethod
    def build_settings(cls):
        """Constructor from django settings"""
        return cls(**{
            f.name: getattr(settings, f.name)
            for f in fields(cls)
            if hasattr(settings, f.name)
        })

    def update_setting(self, name: str, value) -> None:
        """
        Update individual setting
        :param name: Name of setting to update
        :param value: New value for the setting
        """
        self.__setattr__(name, value)


if settings.configured:
    messages_settings = DrfMessagesSettings.build_settings()


@receiver(setting_changed)
def _update_setting(setting=None, value=None, **kwargs):
    if not messages_settings:
        return

    if setting in map(lambda f: f.name, fields(DrfMessagesSettings)):
        messages_settings.update_setting(setting, value)
