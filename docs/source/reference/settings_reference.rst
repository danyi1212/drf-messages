
Settings
--------

MESSAGES_ALLOW_DELETE_UNREAD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| Type ``bool``; Default to ``False``; Not Required.
| Allow users to delete unread message of their own.

By default, users are **forbidden to delete** any unread messages through the Rest API endpoint.
Setting this value to ``True`` will allow users to delete messages haven't already been read.

.. note::
    Users (or rather sessions) have access only to **their messages** only and cannot delete messages that are not their own
    regardless of this setting.

MESSAGES_DELETE_READ
~~~~~~~~~~~~~~~~~~~~

| Type ``bool``; Default to ``False``; Not Required.
| Automatically delete read messages.

When this setting is set to ``True`` each message will be **delete just after it is read**.
This behavior is useful to minimize storage space used by the messages.

When set to ``False``, messages will be deleted either manually or when the appropriate session is cleared.
