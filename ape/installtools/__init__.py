"""utilities to help setup and install pools."""
from __future__ import print_function
import os
import sys
import shutil
import json
from subprocess import call
from .venv import VirtualEnv
from .pool import FeaturePool


def get_ape_venv():
    """Return the _ape virtualenv."""
    return VirtualEnv(os.path.join(os.environ['APE_GLOBAL_DIR'], 'venv'))


def cleanup():
    """Clean up the installation directory."""
    lib_dir = os.path.join(os.environ['CONTAINER_DIR'], '_lib')
    if os.path.exists(lib_dir):
        shutil.rmtree(lib_dir)
    os.mkdir(lib_dir)


def get_project_venv_dir():
    """Return path to project-level venv."""
    return os.path.join(os.environ['CONTAINER_DIR'], '_lib/venv')


def get_or_create_project_venv():
    """
    Create a project-level virtualenv (if it does not already exist).

    :return: ``VirtualEnv`` object
    """
    venv_dir = get_project_venv_dir()

    if os.path.exists(venv_dir):
        return VirtualEnv(venv_dir)
    else:
        return create_project_venv()


def create_project_venv():
    """
    Create a project-level virtualenv.

    :raises: if virtualenv exists already
    :return: ``VirtualEnv`` object
    """
    print('... creating project-level virtualenv')
    venv_dir = get_project_venv_dir()

    if os.path.exists(venv_dir):
        raise Exception('ERROR: virtualenv already exists!')

    use_venv_module = sys.version_info >= (3, 0) and 'APE_USE_VIRTUALENV' not in os.environ

    VirtualEnv.create_virtualenv(venv_dir, use_venv_module=use_venv_module)

    print('... virtualenv successfully created')
    return VirtualEnv(venv_dir)


def get_repo_name(repo_url):
    return repo_url.split('.git')[0].split('/')[-1]


def get_lib_dir():
    return os.path.join(os.environ['CONTAINER_DIR'], '_lib')


def get_pool_dir(repo_name):
    return os.path.join(get_lib_dir(), repo_name)


def fetch_pool(repo_url, branch='master', reuse_existing=False):
    """Fetch a git repository from ``repo_url`` and returns a ``FeaturePool`` object."""
    repo_name = get_repo_name(repo_url)
    lib_dir = get_lib_dir()
    pool_dir = get_pool_dir(repo_name)
    print('... fetching %s ' % repo_name)

    if os.path.exists(pool_dir):
        if not reuse_existing:
            raise Exception('ERROR: repository already exists')
    else:
        try:
            a = call(['git', 'clone', repo_url], cwd=lib_dir)
        except OSError:
            raise Exception('ERROR: You probably dont have git installed: sudo apt-get install git')

        if a != 0:
            raise Exception('ERROR: check your repository url and credentials!')

    try:
        call(['git', 'checkout', branch], cwd=pool_dir)
    except OSError:
        raise Exception('ERROR: cannot switch branches')

    print('... repository successfully cloned')
    return FeaturePool(pool_dir)


def add_to_path(*args):
    print('... adding paths')
    paths = []
    for path in args:
        if type(path) == list:
            paths += path
        else:
            paths.append(path)

    target = os.path.join(os.environ['CONTAINER_DIR'], '_lib/paths.json')
    f = open(target, 'w')
    f.write(json.dumps(paths))
    f.close()
    print('... wrote paths.json')