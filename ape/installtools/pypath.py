from __future__ import print_function, unicode_literals
import os
import json


def get_extra_pypath(container_name=None):
    container_name = container_name or os.environ['CONTAINER_DIR']
    paths_file = '%s/_lib/paths.json' % container_name

    if not os.path.exists(paths_file):
        raise Exception('ERROR: _lib/paths.json does not exist. Did you run ``ape install_container``?')
    else:
        with open(paths_file, 'r') as f:
            return json.loads(f.read())


def generate_pypath_for_initenv():
    separator = ';' if os.name == 'nt' else ':'
    return separator.join(get_extra_pypath()[1:])


if __name__ == '__main__':
    print(generate_pypath_for_initenv())
