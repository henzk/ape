***************************************
Changelog
***************************************

**0.4**

- better errorhandling if virualenv is not installed on debian systems.
- ``bootstrape --dev`` to create an ape container using the development version from github.
- place a file called ``initenv`` in ``APE_ROOT_DIR`` to customize shell environment. The file is sourced on ``activape``.
- spl containers may use their own virtualenv. ``ape`` looks for it in ``_lib/venv`` inside the ``CONTAINER_DIR``.
- added ``aperun`` script to activate a product and call a task in a single step (useful for scripts).
- ``activape mysplcontainer:myproduct`` activates and zaps to mysplcontainer:myproduct in a single step.

**0.3**

- be less verbose
- cleanup environments properly
- improved error propagation
- made the info task a little bit nicer

**0.2**

- first PyPI release

**0.1**

- initial version


