
Rest API Views
=========

Provided with this app is a DRF ViewSet that provides clients to access messages for their session.

Through those endpoints, clients can **list** all of their messages (read and unread), **retrieve** a single message,
and **delete** a message.

Endpoints
---------

:list: GET - List all messages for this session. (``messages:list``)

.. code-block::

    $ curl -X GET "http://127.0.0.1/messages/"

:retrieve: GET - Retrieve specific message from this session. (``messages:retrieve``)

.. code-block::

    $ curl -X GET "http://127.0.0.1/messages/{id}/"

:delete: DELETE - Delete a specific message from this session. (``messages:delete``)

.. code-block::

    $ curl -X DELETE "http://127.0.0.1/messages/{id}/"

.. note::
    By default, clients are **not allowed** to delete messages that are unread.
    You can change this behavior by setting the ``MESSAGES_ALLOW_DELETE_UNREAD`` to ``True`` in your project's settings.

List Filters
------------

This module includes a predefined ``django-filter`` FilterSet.
To use it, simply install ``django-filter`` in your project and the filters will be added automatically.

Install using pip with::

$ pip install django-filter

Then add 'django_filters' to your INSTALLED_APPS:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_filters',
        # ...
    ]

.. seealso::
    To install properly, follow the installation docs at https://django-filter.readthedocs.io/en/stable/guide/install.html

The filters included are:

:unread: Boolean Filter *(true/false)*, show new messages, and vice versa.
:level_tag: Text Filter, minimum message level to show (similar to Python logging handler level).
:level: Integer Filter, show messages filtered by level (with integer lookups).
:extra_tags: Text Filter, messages with specific extra tag (with text lookups).
:view: Text Filter, messages from specific view.
:read_before/after: Date & Time Filter, message read between date and time range.
:created_before/after: Date & Time Filter, message created between date and time range.

Customize the views
-------------------

Those views does not specify any permission classes, authentication classes, filters, pagination, versioning or any other optional extension.

.. warning::
    Users can access only the messages of their **current session**.
    Unauthenticated users can practically access the endpoints, but will always receive an empty list or error 404.

    Providing a permission class like ``IsAuthenticated`` is a good practice, but is not mandatory.

There are mainly two ways to customize those settings, configuring default settings for DRF or creating a custom ViewSet of your own.

Configuration of defaults for your views is done using the ``REST_FRAMEWORK`` setting in your project's ``settings.py`` file.
For example:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        ),
        'DEFAULT_FILTER_BACKENDS': (
            'django_filters.rest_framework.DjangoFilterBackend',
            'rest_framework.filters.SearchFilter',
            'rest_framework.filters.OrderingFilter',
        ),
        'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
        'PAGE_SIZE': 10,
    }

.. note::
    Note that ``django_filters`` is included in this example, and needs to be installed before use.

.. seealso::
    See more in the Django Rest Framework docs https://www.django-rest-framework.org/api-guide/settings/

Alternatively, you can create your oen version of the ``MessagesViewSet`` and use it instead.

First at your ``views.py`` create a new ViewSet that extends the ``MessagesViewSet`` class.

.. code-block:: python
    :emphasize-lines: 5

    from rest_framework.pagination import LimitOffsetPagination
    from rest_framework.permissions import IsAuthenticated
    from django_filters.rest_framework import DjangoFilterBackend

    from drf_messages.views import MessagesViewSet


    class MyMessagesViewSet(MessagesViewSet):
        permission_classes = (IsAuthenticated,)
        pagination_class = (LimitOffsetPagination,)
        filter_backends = (DjangoFilterBackend,)


Then at your ``urls.py`` create a router, register your custom view, and attach it to the ``urlpatterns``.
For example:

.. code-block:: python
    :emphasize-lines: 6

    from rest_framework.routers import DefaultRouter

    from myapp.views import MyMessagesViewSet

    router = DefaultRouter()
    router.register("messages", MyMessagesViewSet, "messages")


    app_name = "myapp"
    urlpatterns = [
        *router.urls,
    ]

