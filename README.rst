drf-messages
============

.. image:: https://readthedocs.org/projects/drf-messages/badge/?version=latest
    :target: https://drf-messages.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/Maintained-yes-green.svg
    :target: https://github.com/danyi1212/drf-messages/graphs/commit-activity
    :alt: Maintained

.. image:: https://static.pepy.tech/personalized-badge/drf-messages?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads&service=github
    :target: https://pepy.tech/project/drf-messages

**Use Django's Messages Framework with Django Rest Framework.**

| Documentation is available at https://drf-messages.readthedocs.io/en/latest/
| PyPI Package at https://pypi.org/project/drf-messages/
| Django Packages at https://djangopackages.org/packages/p/drf-messages/

Requirements:

- Python (3.6, 3.7, 3.8, 3.9)
- Django (2.2, 3.0, 3.1)
- Django Rest Framework (3.0-3.12)

Django's message framework is awesome, and now its even better with Django Rest Framework!

The django's messages framework is a very easy and quick way to provide one-time messages for the user.
When using django rest framework you loose most of the functionality of it.
Using this app you can access your messages though a rest api endpoint.

Features
~~~~~~~~
- Persistent message storage in database
- Automatic cleanup
- DRF endpoint for accessing messages

Quick Start
-----------

1. Install using:

.. code-block::

    $ pip install drf-messages

2. Configure project ``settings.py``:

.. code-block:: python

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

Any unread messages will have ``read_at`` as ``null``.
If you have ``django-filter`` configured, you can also query "http://localhost/messages/?unread=true" to get only unread messages.

Getting help
------------

In case you have trouble while using this module, you may use the `GitHub Disccussion <https://github.com/danyi1212/drf-messages/discussions>`_.

For any bug or issue, open a `new GitHub Issue <https://github.com/danyi1212/drf-messages/issues>`_.

Contributing
------------
