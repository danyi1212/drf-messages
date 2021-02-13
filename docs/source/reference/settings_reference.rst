
Settings
--------

MESSAGES_USE_SESSIONS
~~~~~~~~~~~~~~~~~~~~~

| Type ``bool``; Default to ``False``; Not Required.
| Use session context to store messages.

Store and query messages for current session only.
When is set to ``True`` messages are added only to the current session, and is shown only to throughout the session.

By default, messages are stored with user context.
That means the user can see all their messages everywhere.

.. note::
    Using user context messages can **support authentication backends** other then ``SessionAuthentication``,
    while session messages is better for showing messages **only where they are relevant** and
    **automatic cleaning** stale messages as the session deletes on expire or logoff.

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
