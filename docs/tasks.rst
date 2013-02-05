.. _task-functions:

Task functions
=====================

Tasks are python functions that are typically defined in the ``tasks`` module of a feature.
Other features can refine tasks to adapt their behaviour.
``ape`` automatically creates a command line parser for every task, by inspecting the function signature.

``ape`` concentrates solely on task definition, refinement, and invokation from the command line.
It does not contain any helpers for implementing your tasks ---
there are plenty good packages out there to support you with that:

- ``subprocess``, ``os``, ``sys`` in the Python standard library
- http://amoffat.github.com/sh/
- `Fabric <http://fabfile.org>`_, https://github.com/sebastien/cuisine
- ... lots of others

Introducing tasks
-----------------------

Tasks are introduced by implementing the task as a python function in your
feature`s ``tasks`` module. The function must be decorated with ``ape.tasks.register`` to become a task::

    #myfeature/tasks.py

    from ape import tasks

    @tasks.register
    def mynewtask(a, b, c=1):
        """description of mynewtask"""
        print a, b, c


To make the task available from the command line, we need to select ``myfeature`` by setting the ``PRODUCT_EQUATION``
shell variable::

    $ export PRODUCT_EQUATION="myfeature"


Now, make sure ``mynewtask`` is listed in the output of::

    $ ape help

Finally, let`s invoke it::

    $ ape mynewtask 1 2 --c 5
    1 2 5
    $ ape mynewtask 1 2
    1 2 1

Refining a task
--------------------

Here, we refine ``mynewtask`` in another feature.
To do that, we need to specify a higher order function called ``refine_mynewtask`` that returns the refined task function.
The refined function can access the original implementation as ``original``.

::

    #anotherfeature/tasks.py

    def refine_mynewtask(original):
        def mynewtask(a, b, c=7):
            """updated description of mynewtask"""
            print 'refined task'
            original(a, b, c=c)
        return mynewtask


So, to refine a task, we need to define a "factory" that accepts the original task
as parameter and returns a wrapper ---the refined task.
The factory must be named ``refine_`` followed by the name of the task to refine --- in the example above, this results in ``refine_mynewtask``.
When the feature composer encounters this function, it applies the refinement.

``ape`` uses ``featuremonkey`` to compose the feature modules.
For a more detailed description on the composition process, please see the ``featuremonkey`` documentation at http://featuremonkey.readthedocs.org\ .

.. note:

    Tasks can be refined by multiple features. Then, the composition order ---the order in which the wrappers are applied--- may matter!

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


Running ape
----------------


