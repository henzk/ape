.. _modes-of-operation:

********************
Modes of Operation
********************

**container mode**

In container mode, ``ape`` manages your features and products in a directory structure.
It provides special tasks to switch between products.

**standalone mode**

In standalone mode, ``ape`` checks the environment variable ``PRODUCT_EQUATION`` to get the list of features in composition order.
Use container mode! This is for development of ape.


Container Mode
=====================

In container mode, ``ape`` manages your features and products in a directory structure.
It provides special tasks to switch between products.

All files managed by ``ape`` are placed inside a directory that we will refer to as ``APE_ROOT_DIR`` in the following.
If you followed the installation instructions, this folder is called ``aperoot``.

It contains:

- a directory named ``_ape``. This directory contains the activation script and other global ressources like the global virtualenv.
- multiple *SPL Containers*. These are installations of specific versions of software product lines you manage using ``ape``.


Tasks in container mode
---------------------------


**cd** *poi*

cd to a container or product inside a container.
``poi`` is a string in one of these formats:

- ``<container_name>`` e.g. ``ape cd mycontainer``
- ``<container_name>:<product_name>`` e.g. ``ape cd mycontainer:myproduct``


**switch** *poi*

activate the environment of product specified by ``poi``
``poi`` is a string in this format:

- ``<container_name>:<product_name>`` e.g. ``ape switch mycontainer:myproduct``


**teleport** *poi*

``ape switch`` and ``ape cd`` in one operation.

``poi`` is a string in this format:

- ``<container_name>:<product_name>`` e.g. ``ape teleport mycontainer:myproduct``

Since ``teleport`` is quite long, and it`s all about productivity, ``zap`` is available as an alias for ``teleport`` ;)


Standalone Mode
=====================

In standalone mode, ``ape`` checks the environment variable ``PRODUCT_EQUATION`` to get the list of features in composition order.

It needs to contain the names of the features seperated by spaces, e.g. ``"basic_tasks extra_tasks my_adjustments"``.
For details on how features are specified, see :ref:`feature-modules`.

Feature modules need to be placed on the ``PYTHONPATH`` so ``ape`` can find them.
In container mode, ``ape`` can manage that for you.

