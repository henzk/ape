##########################################
Welcome to ape's documentation!
##########################################

.. epigraph::

    ``ape`` is a make/rake/ant/fab-like system with support for FOSD.


``ape`` is short for "A Productive Environment". It provides a way to organize tasks in feature modules.
Feature modules can introduce new tasks and refine tasks that have been introduced by other features.

Tasks are defined as simple python functions. ``ape`` makes these task functions available from the command line
and provides usage information by extracting the functions` docstrings.

******************
Overview
******************

``make`` looks for a ``Makefile`` in your current directory that defines the available tasks.
In Contrast, ``ape`` composes the available tasks from a list of selected feature modules.

``ape`` provides two basic modes of operation, that make different assumptions on how features are selected:

- in *standalone mode* (default) features need to be placed somewhere on the ``PYTHONPATH``.
- in *container mode* ``ape`` provides a set of conventions to organize features and products in a directory structure.

For details, see :ref:`modes-of-operation`.

Specifying tasks is really simple: you implement your task as a simple python function.
Other features can contain refinements for tasks. This way, it is possible to adapt the behaviour of specific tasks
depending on the feature selection. For details, see :ref:`task-functions`.



***************************************
Contents
***************************************

.. toctree::
    :maxdepth: 2

    install
    modes
    features
    tasks
    tutorial
    changelog


*********************
Indices and tables
*********************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


