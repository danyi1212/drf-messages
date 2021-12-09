
Change Log
==========

1.1.1
-----

Release date: 9 Dec, 2021

- **ADDED** Support for all session engines (not only DB engine) See docs for :docs:`settings_reference`

.. warning::
    This version **requires migration** after upgrade from older version


1.1.0
-----

Release date: 2 Dec, 2021

- **ADDED** Support for Django 3.2
- **NEW** Methods for Message model. See docs for :doc:`models`
- **NEW** Collection-like interface for Storage objects. See docs for :doc:`storage`
- **NEW** CI/CD for testing, linting and deploying
- **BUG FIX** Messages incorrectly marked read after using list endpoint
- **BUG FIX** Errors when querying messages from request without a session

1.0.1
-----

Release date: 24 Feb. 2021

- **NEW** Peak messages endpoint


1.0.0
-----

Release date: 13 Feb. 2021

- First published version

