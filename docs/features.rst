.. _feature-modules:

Feature modules
====================

Layout
-------------

Feature modules are Python Packages that contain a module called ``tasks``, so a minimal feature called ``myfeature`` would look like this::

    myfeature/
        __init__.py
        tasks.py

Feature modules need to be placed on the ``PYTHONPATH``.

When using container mode, this part is managed for you.

