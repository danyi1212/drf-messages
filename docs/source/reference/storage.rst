
Storage
=======
Storage can be accessed using ``django.contrib.message.get_messages`` method.
For example:

.. code-block:: python

    from django.contrib.messages import get_messages

    storage = get_messages(request)

Attributes
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


Python Access
~~~~~~~~~~~~~~

The storage object provide many syntax based access that is similar to other **Python collections**.
All access via those interfaces is for **unread messages**, and some of them also **mark them as read**.

+-------------------------------+------+---------------------------------------------------+
| Example                       | Read | Explanation                                       |
+===============================+======+===================================================+
| ``[m for m in storage]``      | ✅   | Retrieve messages lazily                          |
+-------------------------------+------+---------------------------------------------------+
| ``storage[1]``                | ✅   | Get specific message from storage                 |
+-------------------------------+------+---------------------------------------------------+
| ``storage[:5]``               | ✅   | Get subset of messages (slice)                    |
+-------------------------------+------+---------------------------------------------------+
| ``if storage:``               | ❌   | Check if there are unread messages                |
+-------------------------------+------+---------------------------------------------------+
| ``len(storage)``              | ❌   | Get count if unread messages                      |
+-------------------------------+------+---------------------------------------------------+
| ``Message() in storage``      | ❌   | Check if a message exists and is unread           |
+-------------------------------+------+---------------------------------------------------+
| ``"Message Body" in storage`` | ❌   | Check if an unread message with that text exists  |
+-------------------------------+------+---------------------------------------------------+
| ``messages.INFO in storage``  | ❌   | Check if an unread message with that level exists |
+-------------------------------+------+---------------------------------------------------+
| ``str(storage)``              | ✅   | Get all messages, divided by comma                |
+-------------------------------+------+---------------------------------------------------+
| ``repr(storage)``             | ❌   | Get all messages, divided by comma                |
+-------------------------------+------+---------------------------------------------------+

.. warning::
    When **iterating** over storage, the marking of messages as read is done after iteration is over. 
    When iteration is complete **all unread messages will be marked as read**, whether they were returned during iteration or not.

Methods
~~~~~~~

:get_queryset(): Get queryset of all messages for that request.
:get_unread_queryset(): Get queryset of unread messages for that request.
:add(level, message, extra_args): Add a new message to the storage.
:update(response): Perform deleting procedure manually.
