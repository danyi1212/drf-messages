
Installation
============

| This is a **detailed** walk-through the *drf-messages* installation and setup process.
| For easy and quick installation please refer to the :doc:`quick_start` guide.

Getting it
----------
You can get ``drf-messages`` by using pip::

 $ pip install drf-messages

If you want to install it from source, grab the git repository and run setup.py::

$ git clone https://github.com/danyi1212/drf-messages.git
$ python setup.py install

Dependencies
------------

Django Rest Framework is an **optional dependency** of this module.
It is required only for the provided views and serializers.

Install using pip with::

$ pip install djangorestframework

If you are only planning to use the persistent storage and do not need the provided view, you can skip the installation of Django Rest Framework.

.. seealso::
    To install it properly visit the installation docs at https://www.django-rest-framework.org/#installation

Installing
----------

First, you will need to add the ``drf_message`` application to the ``INSTALLED_APPS`` setting in you Django project ``settings.py`` file.

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django.contrib.sessions',
        'django.contrib.messages',
        'rest_framework',  # optional
        'drf_messages',
        # ...
    ]


.. note::
    Note that both of Django's ``messages`` and ``sessions`` contrib apps are required for this module.
    Make sure to include them in your ``INSTALLED_APPS`` too:

It is suggested to verify that both ``messages`` and ``sessions`` middlewares are installed.
The configuration should look like so:

.. code-block:: python

    MIDDLEWARE = [
        # ...
        'django.contrib.sessions.middleware.SessionMiddleware',
        # ...
        'django.contrib.messages.middleware.MessageMiddleware',
        # ...
    ]

.. seealso::
    Read the Django's messages framework docs for more information at https://docs.djangoproject.com/en/3.1/ref/contrib/messages/

.. warning::
    Only database-backed sessions are compatible with this module.

After installing the new app, you will need to **run migration** to create the new database tables::

$ py manage.py migrate drf_messages

If you have more apps with pending migrations, you may want to omit the ``drf_messages`` argument and run all pending migrations together.

Next, you will want to **configure** the messages storage to use the ``DBStorage`` class.
This is done using the ``MESSAGE_STORAGE`` setting in your project's ``settings.py`` file:

.. code-block:: python

    MESSAGE_STORAGE = "drf_messages.storage.DBStorage"

The last configuration is the addition of the the **messages views** to the router.
This is done by including the ``drf_messages.urls`` to the urlpatterns in your project's ``urls.py``.

.. code-block:: python

    urlpatterns = [
        path('messages/', include('drf_messages.urls')),
    ]

The views can be added anywhere throughout your project, at any path that fits your desires.

.. note::
    This part requires ``djangorestframework`` to be installed.
