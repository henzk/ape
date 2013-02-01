##########################################
Welcome to ape's documentation!
##########################################

    ``ape`` is a make/rake/ant/fab-like system with support for FOSD.

``ape`` is short for "A Productive Environment".

******************
Introduction
******************

``make`` looks for a ``Makefile`` in your current directory that defines the available tasks.

``ape`` composes the available tasks from a list of feature modules.
Feature modules can introduce new tasks and refine tasks that have been introduced by other features.

``ape`` provides two basic modes of operation, that define how 

- **standalone mode**

In standalone mode, ``ape`` checks the environment variable ``PRODUCT_EQUATION`` to get the list of features in composition order.
It needs to contain the names of the features seperated by spaces, e.g. ``"basic_tasks extra_tasks my_adjustments"``.

..

    If ``ape`` cannot find the ``PRODUCT_EQUATION`` environment variable, TODO


- **container mode**

In container mode, ``ape`` manages your features and products in a directory structure.


Example
===============

Problem
------------

Suppose you have multiple computers with slightly different installations:

**Office Computer**

- you use ``acroread`` to view pdf documents
- documents are released by placing them into ``~/public-html/documents/``


**Home Computer**


**Notebook**



***************************************
Getting started
***************************************

.. toctree::
    :maxdepth: 2
    
    install
    tutorial

***************************************
featuremonkey Reference
***************************************

.. toctree::
    :maxdepth: 2
    
    reference


***************************************
Changelog
***************************************

**HEAD**



**0.1**

- initial version


*********************
Indices and tables
*********************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


