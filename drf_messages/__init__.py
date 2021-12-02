import logging

import django


__title__ = "DRF Messages"
__version__ = "1.1.0"
__author__ = "Dan Yishai"
__license__ = "BSD 3-Clause"


logger = logging.getLogger("drf_messages")

if django.VERSION < (3, 2):
    default_app_config = "drf_messages.apps.DrfMessagesConfig"
