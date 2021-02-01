
Quick Start
===========

1. Install using:

.. code-block::

    $ pip install drf-messages

2. Configure project ``settings.py``:

.. code-block:: python
    :emphasize-lines: 5, 9

    INSTALLED_APPS = [
        # ...
        'django.contrib.messages',
        'rest_framework',
        'drf_messages',
        # ...
    ]

    MESSAGE_STORAGE = "drf_messages.storage.DBStorage"

4. Configure routes at your project's ``urls.py``

.. code-block:: python

    urlpatterns = [
        path('messages/', include('drf_messages.urls')),
        # ...
    ]

3. Run migrations using:

.. code-block::

    $ py manage.py migrate drf_messages

For more details visit the docs for installation: https://drf-messages.readthedocs.io/en/latest/installation/installation.html

Usage
-----

You can list all your messages with::

$ curl -X GET "http://localhost/messages/"

Any unseen messages will have ``seen_at`` as ``null``.
If you have ``django-filter`` configured, you can also query "http://localhost/messages/?seen_at=null" to get only new messages.
