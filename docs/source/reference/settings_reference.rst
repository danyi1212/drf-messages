
Settings
--------

MESSAGES_USE_SESSIONS
~~~~~~~~~~~~~~~~~~~~~

| Type ``bool``; Default to ``False``; Not Required.
| Use session context to query messages.

Query messages for current session only.
When is set to ``True``, only messages created from the **same session** will be shown.

By default (``False``), messages are queried only by the **authenticated user**.
That means the user can see all their messages from **all sessions**.

Relating messages to session is different according to your configured `Session Engine <https://docs.djangoproject.com/en/dev/ref/settings/#session-engine>`_.
For the most part, the ``session_key`` string is used to filter the query.
When is available, the ``Session`` model object is used as `ForeignKey` and is also used to filter the query.

.. note::
    When using a session engine that works with db ``Session`` model, you unlock extra functionality that **automatically
    clears out messages** after user logout or `clearsessions <https://docs.djangoproject.com/en/3.2/topics/http/sessions/#clearing-the-session-store>`_ command.

Tested session engines:

* ``django.contrib.sessions.backends.db`` (uses db)
* ``django.contrib.sessions.backends.file``
* ``django.contrib.sessions.backends.cache``
* ``django.contrib.sessions.backends.cached_db`` (uses db)
* ``django.contrib.sessions.backends.signed_cookies``
* ``redis_sessions.session`` (`django-redis-sessions <https://github.com/martinrusev/django-redis-sessions>`_)


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
