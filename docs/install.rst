**************************
Installation
**************************

There are multiple options to get ape to run on your system.
When using container mode, ``ape`` is installed in a virtualenv inside the container root.
This is the recommended way to use ``ape``.

If you need to start over, simply delete the container root
and recreate it again.


Bootstrapping a container mode environment
==============================================

Make sure you have ``pip`` and ``virtualenv`` installed.
If not, try:

    $ easy_install pip
    $ pip install virtualenv

On Debian/Ubuntu, these are also available as system packages ``python-pip`` and ``python-virtualenv``.

Fetch the script to bootstrap ``ape`` in container mode::

    $ wget https://raw.github.com/henzk/ape/master/bin/bootstrape
    $ chmod 0755 bootstrape


Now, run ``bootstrape`` to create the container structure in a folder called ``aperoot``\ (change this to your liking)::

    $ bootstrape aperoot

To install the development version, run this instead::

    $ bootstrape --dev aperoot

After the process has finished a folder ``aperoot`` is available. It contains all necessary files and dependencies.
A virtualenv has been created at ``aperoot/_ape/venv``.
To activate the container mode, source the activation script for ``ape`` in your shell (requires bash)::

    $ . aperoot/_ape/activape

Congratulations! ``ape`` is now installed and container mode is activated.


.. note::

    The ``bootstrape`` script creates the necessary folder structure, creates a virtualenv,
    and installs ``ape`` into that environment. There, the latest stable/development version of ``ape`` is used ---
    even if you used the ``bootstrape`` script of another version!

    To use a custom version of ``ape`` in container mode,
    simply uninstall ``ape`` from the virtualenv and install your custom version instead.



Installing ape globally
=========================

.. warning::

    The preferred method of installing ape is to use bootstrape as described above. Installing ape globally means you have to create the ape root directory manually.
    Use this only if you want to hack on ape.


To install the latest version of ``ape``, use ``pip``::

    $ pip install ape


To get the development version of ``ape`` directly from github, use::

    $ pip install git+https://github.com/henzk/ape.git#egg=ape


Now, ``ape`` should be available on your ``PATH``::

    $ ape
    Error running ape:
    Either the PRODUCT_EQUATION or PRODUCT_EQUATION_FILENAME environment variable needs to be set!


