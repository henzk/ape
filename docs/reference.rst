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

Here, we refine ``mynewtask`` in another feature.
To do that, we need to specify a higher order function called ``refine_mynewtask`` that returns the refined function.
The refined function can access the original implementation as ``original``.

::

    #anotherfeature/tasks.py

    def refine_mynewtask(original):
        def mynewtask(a, b, c=7):
            """updated description of mynewtask"""
            print 'refined task'
            original(a, b, c=c)
        return mynewtask


``ape`` uses ``featuremonkey`` to compose the feature modules.
For a more detailed description on the composition process, please see the ``featuremonkey`` documentation at http://featuremonkey.readthedocs.org\ .


Calling other tasks
--------------------

Often, tasks need to call other tasks. Functions decorated with ``ape.tasks.register`` cannot be called directly.
This is a safety mechanism to protect against calling partially composed tasks.

To call another task called ``mynewtask`` call ``ape.tasks.mynewtask``::


    #somefeature/tasks.py

    @tasks.register
    def taskcallingtask():
        #call mynewtask
        tasks.mynewtask(1, 2, c=3)


