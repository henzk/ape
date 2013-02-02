ape Reference
======================

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

.. _task-functions:

Task functions
=====================

Introduction of Tasks
-----------------------

Tasks are introduced by implementing the task as a python function in your
feature`s ``tasks`` module decorated with ``ape.tasks.register``::

    #myfeature/tasks.py

    from ape import tasks

    @tasks.register
    def mynewtask(a, b, c=1):
        """description of mynewtask"""
        print a, b, c


To make the task available from the command line, we need to select ``myfeature`` by setting the ``PRODUCT_EQUATION``
shell variable::

    export PRODUCT_EQUATION="myfeature"


Now, make sure ``mynewtask`` is listed in the output of::

    ape help

Finally, let`s invoke it::

    ape mynewtask 1 2 --c 5


Refinement of Tasks
--------------------

::

    #anotherfeature/tasks.py

    def refine_mynewtask(original):
        def mynewtask(a, b, c=7):
            """updated description of mynewtask"""
            print 'refined task'
            original(a, b, c=c)
        return mynewtask



Calling other tasks
--------------------

::

    #somefeature/tasks.py

    @tasks.register
    def taskcallingtask():
        #call mynewtask
        tasks.mynewtask(1, 2, c=3)


