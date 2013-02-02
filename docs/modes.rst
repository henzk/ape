.. _modes-of-operation:

********************
Modes of Operation
********************

**standalone mode**

In standalone mode, ``ape`` checks the environment variable ``PRODUCT_EQUATION`` to get the list of features in composition order.

**container mode**

In container mode, ``ape`` manages your features and products in a directory structure.
It provides special tasks to switch between products.

Standalone Mode
=====================

In standalone mode, ``ape`` checks the environment variable ``PRODUCT_EQUATION`` to get the list of features in composition order.

It needs to contain the names of the features seperated by spaces, e.g. ``"basic_tasks extra_tasks my_adjustments"``.
For details on how features are specified, see :ref:`feature-modules`.

Feature modules need to be placed on the ``PYTHONPATH`` so ``ape`` can find them.
In container mode, ``ape`` can manage that for you.

Container Mode
=====================

In container mode, ``ape`` manages your features and products in a directory structure.
It provides special tasks to switch between products.

All files managed by ``ape`` are placed inside a directory that we will refer to as ``APE_ROOT_DIRECTORY`` in the following.
It contains:

- a directory named ``_ape``. It contains the activation script and other global ressources.
- multiple *SPL Containers*. These are installations of specific versions of software product lines you manage using ``ape``.



Tasks in container mode
---------------------------


**cd**


**switch**


**teleport**




