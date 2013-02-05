**************************
Installation
**************************

There are multiple options to get ape to run on your system.
When using container mode, ``ape`` is installed in a virtualenv inside the container root.
This is the recommended way to testdrive ``ape``. If you need to start over, simply delete the container root
and recreate it again. Container root creation is referred to as bootstrapping in the following.

If you plan on using multiple container mode setups on the same machine or want to use ``ape`` in standalone
mode only, it also makes sense to install ``ape`` globally.

Installing ape globally
=========================

To install the latest version of ``ape``, use ``pip``::

    $ pip install ape


To get the development version of ``ape`` directly from github, use::

    $ pip install git+https://github.com/henzk/ape.git#egg=ape


Now, ``ape`` should be available on your ``PATH``::

    $ ape
    Error running ape:
    Either the PRODUCT_EQUATION or PRODUCT_EQUATION_FILENAME environment variable needs to be set!


Bootstrapping a container mode environment
==============================================

Make sure you have ``pip`` and ``virtualenv`` installed.
If not, try:

    $ easy_install pip
    $ pip install virtualenv

On Debian/Ubuntu, these are also available as system packages ``python-pip`` and ``python-virtualenv``.

If ``ape`` is not already installed globally, we need to fetch the script to bootstrap ``ape`` in container mode::

    $ wget https://raw.github.com/henzk/ape/master/bin/bootstrape
    $ chmod 0755 ./bootstrape

Now, run ``bootstrape`` to create the container structure in a folder called ``aperoot``::

    $ ./bootstrape aperoot

If you have installed ``ape`` globally, ``bootstrape`` is already available. Then, simply execute::

    $ bootstrape aperoot


After the process has finished a folder ``aperoot`` is available. It contains all necessary files and dependencies.
A virtualenv has been created at ``aperoot/_ape/venv``.
To activate the container mode, source the activation script for ``ape`` in your shell (requires bash)::

    $ . aperoot/_ape/activape

``ape`` is now installed and container mode is activated.


.. note::

    The ``bootstrape`` script creates the necessary folder structure, creates a virtualenv,
    and installs ``ape`` into that environment. There, the latest stable version of ``ape`` is used ---
    even if you used the ``bootstrape`` script of another version!

    To use a custom version of ``ape`` in container mode,
    simply uninstall ``ape`` from the virtualenv and install your custom version instead.
