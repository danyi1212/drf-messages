
Storage
=======

Storage can be access using ``django.contrib.message.get_messages`` method.
For example:

.. code-block:: python

    from django.contrib.messages import get_messages

    storage = get_messages(request)

Properties
~~~~~~~~~~

:level: Minimum message level.
Can be modified to specify custom minimum message level.
For example:

.. code-block:: python
    :emphasize-lines: 3,6

    from django.contrib import messages

    messages.set_level(request, messages.DEBUG)
    # is the same as
    storage = messages.get_messages(request)
    storage.level = messages.DEBUG

:used: Indicates the storage was used.
You may set to ``False`` to avoid the message deletion procedure.

.. code-block:: python
    :emphasize-lines: 7

    from django.contrib import messages

    storage = messages.get_messages(request)
    for message in storage:
        print(message)

    storage.used = False

.. seealso::
    More information in the django's messages framework docs
    https://docs.djangoproject.com/en/3.1/ref/contrib/messages/#expiration-of-messages

Methods
~~~~~~~

:get_queryset(): Get queryset of all messages for that request session.
:get_unread_queryset(): Get queryset of unread messages for that request session.
:add(level, message, extra_args): Add a new message to the storage.
:update(response): Perform deleting procedure manually.

Special methods
~~~~~~~~~~~~~~~

:__contains__: Checks if there is an unread message with same text and level for that request session.
:__len__: Count of unread message for that request session.
:__iter__: Iterate over django's message framework's Message objects (messages are marked as seen).
:__enter__: Returns self.
:__exit__: Marks all unread messages as read now.