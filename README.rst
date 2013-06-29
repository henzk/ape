ape - a productive environment
==============================

.. image:: https://secure.travis-ci.org/henzk/ape.png
   :target: http://travis-ci.org/henzk/ape

.. epigraph::

    ``ape`` is a make/rake/ant/fab-like system with support for FOSD.


``ape`` is short for "A Productive Environment". It provides a way to organize tasks in feature modules.
Feature modules can introduce new tasks and refine tasks that have been introduced by other features.

Tasks are defined as simple python functions. ``ape`` makes these task functions available from the command line
and provides usage information by extracting the functions' docstrings.

``ape`` can be used to manage software product lines(SPL). SPLs are placed in containers that contain their features and products.

Documentation: http://ape.readthedocs.org/

License: MIT
