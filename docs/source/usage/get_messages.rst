
Access Messages
===============

This module keeps the **same interface** of the vanilla Django's messages framework, and can be used just like
shown in the Django docs at https://docs.djangoproject.com/en/3.1/ref/contrib/messages/.

Create a new message
~~~~~~~~~~~~~~~~~~~~

Creating a new message is as straight forward as this:

.. code-block:: python

    from django.contrib import messages

    messages.info(request, 'Hello world!')

In this example, an information message is created for that ``request`` object.

.. warning::
    In case the request has **no user or session** provided, the message will be stored in memory
    for **temporary storage** available through that request processing.
    Messages added that are not used until the response will not be available anymore.

Extra tags can be attached to the message, as a string or list of strings.
For example:

.. code-block:: python

    from django.contrib import messages

    messages.info(request, 'Hello world!', extra_tags="debug")
    messages.info(request, 'Hello world!', extra_tags=["debug", "test"])

Those extra tags will be save with the message and can be used for filtering, rendering or any other use you can think of.

About the levels
----------------

The django's messages framework uses **configurable level architecture** similar to that of the Python logging module.
Each message provide a integer level that is represented by a tag, and can be used to group messages by type, filtered or to be rendered differently.

This module keeps the same architecture.

The django's messages framework provides a default of 5 levels.
This can be configured using the ``MESSAGE_TAGS`` setting.
For example:

.. code-block:: python
    :emphasize-lines: 7

    MESSAGE_TAGS = {
        10: 'debug',
        20: 'info',
        25: 'success',
        30: 'warning',
        40: 'error',
        50: 'critical',
    }


.. note::
    | Modifying this setting will affect the ``MessageSerializer`` and alter the Rest API schema.
    | Additionally, the Messages admin will list the new tags as select options for level.

When doing so, you will need to **manually** create a new message (the default shortcuts will not suit you).
It is advised to store any custom level in a **constant variable** for a more readable code.
For example:

.. code-block:: python
    :emphasize-lines: 5

    from django.contrib import messages

    CRITICAL = 50

    messages.add_message(request, CRITICAL, 'Hello world!')

Using those message levels, you can set a **minimum level**, so that any message with a lower level will be **ignored** and
will not be saved.

Configuring minimum level can be done at the project level via the ``MESSAGE_LEVEL`` setting.
For example:

.. code-block:: python

    MESSAGE_LEVEL = 20
    # (this is the actual default value)

Alternatively, it can be configured per request:

.. code-block:: python
    :emphasize-lines: 4,8,13

    from django.contrib import messages

    # Change the messages level to ensure the debug message is added.
    messages.set_level(request, messages.DEBUG)
    messages.debug(request, 'Test message...')

    # In another request, record only messages with a level of WARNING and higher
    messages.set_level(request, messages.WARNING)
    messages.success(request, 'Your profile was updated.') # ignored
    messages.warning(request, 'Your account is about to expire.') # recorded

    # Set the messages level back to default.
    messages.set_level(request, None)

.. seealso::
    From the django docs https://docs.djangoproject.com/en/3.1/ref/contrib/messages/#changing-the-minimum-recorded-level-per-request

Reading messages
~~~~~~~~~~~~~~~~

Sometimes it is useful to **access and read** the messages directly in your code.

Accessing the messages can be performed exactly with the **same interface** as the default Django messages framework, but with some extra flairs.

The vanilla ways to access the messages is inside templates:

.. code-block::
    :emphasize-lines: 3

    {% if messages %}
        <ul class="messages">
            {% for message in messages %}
            <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>
                {% if message.level == DEFAULT_MESSAGE_LEVELS.ERROR %}Important: {% endif %}
                {{ message }}
            </li>
            {% endfor %}
        </ul>
    {% endif %}

Another classic way is iterating over the messages storage:

.. code-block:: python
    :emphasize-lines: 4

    from django.contrib.messages import get_messages

    storage = get_messages(request)
    for message in storage:
        print(message)


.. note::
    When using the traditional interface specified above, all messages will be **marked as read** immediately.

The storage object behaves almost like any other collection. You can get message at a **specific index**, **slice** it,
check its **length**, etc. See more in the reference for :doc:`../reference/storage`.

.. code-block:: python

    from django.contrib.messages import get_messages

    storage = get_messages(request)
    first_five_messages = storage[:5]
    if storage:
        message = storage[0]



Alternatively, this module provides a **QuerySet access** to the messages.

It includes **extra information** in the messages, like ``created``, ``read_at`` and ``view`` to specify the creation time,
when read (or null if unread), and the view who submitted the message respectively.
Using the QuerySet you will have all it's features like filtering, aggregations, etc.

This can be access through the storage, for example:

.. code-block:: python
    :emphasize-lines: 4-5

    from django.contrib.messages import get_messages

    storage = get_messages(request)
    queryset = storage.get_queryset()  # all messages
    unread_queryset = storage.get_unread_queryset()  # unread messages only

.. warning::
    When using the queryset interface, it is important to **mark as seem** all queried messages after use.

After every access, you will probably want to **mark those messages as read** in order to allow them to be cleared from the database.

This can be done manually like so:

.. code-block:: python
    :emphasize-lines: 6

    from django.contrib.messages import get_messages

    storage = get_messages(request)
    queryset = storage.get_unread_queryset()
    # do something with the messages...
    queryset.mark_read()

Alternatively, you can use the ``with`` operator on the storage to mark all messages as read on block exit.
For example:

.. code-block:: python
    :emphasize-lines: 4

    from django.contrib.messages import get_messages

    storage = get_messages(request)
    with get_messages(request) as storage:
        queryset = storage.get_unread_queryset()
        # do something with the messages...

.. note::
    When **no session** is available in the request, the messages are saved in a **temporary storage** in memory and
    can be accessed **only throughout the same request/response process**.

    In this scenario, **only legacy interface** is available.
    That means all queryset related features, such as ``get_queryset()``, ``get_unread_queryset()``, ``mark_read()``
    and the ``with`` operator will not do practically anything.

Deleting messages
~~~~~~~~~~~~~~~~~

When using a persistent message storage, it is important to implement procedure for **clearing out** old messages.

When using sessions, messages get cleared automatically only when the **appropriate session is deleted** from database
due to user logout or ``clearsessions`` command.

This behavior is not affected by the ``MESSAGES_USE_SESSIONS`` setting.
As long as there is a session provided with the request, all the messages will be cleared when the session is cleared.

.. note::
    Make sure to regularly run the ``clearsessions`` command to delete any expired session and clear stale messages.
    See more at the django docs https://docs.djangoproject.com/en/3.1/topics/http/sessions/#clearing-the-session-store

If you are **not using Session Authentication**, it is advised to setup a manual message clearing procedure,
such as a scheduled deletion of all read messages created before a certain time.

Additionally, you may want to configure the ``MESSAGE_DELETE_READ`` setting to ``True`` at your project's ``settings.py`` file.
This setting will cause any read message to be **deleted just after the request is done processing**.

Another way is to **delete messages manually** in you code.
This can be done using the QuerySet interface to messages:

.. code-block:: python
    :emphasize-lines: 6

    from django.contrib.messages import get_messages

    storage = get_messages(request)
    queryset = storage.get_queryset()
    # delete only messages that have already been read
    queryset.filter(read_at__isnull=False).delete()

.. note::
    Make sure not to delete unread messages before the user gets a chance or getting them...