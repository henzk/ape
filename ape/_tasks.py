"""
APE - a productive environment


"""
from __future__ import print_function

# Tasks specified here are available globally.
#
# WARNING: importing ape.tasks at the module level leads to a cyclic import for
#  global tasks in this file, so import it inside the task function.
#  The effect is specific to this file - you may import ape.tasks directly
#  at the module level in tasks modules of features.
#

FEATURE_SELECTION = []


def help(task):
    '''print help on specific task'''
    from ape import tasks
    tasks.help(taskname=task)


def explain_feature(featurename):
    '''print the location of single feature and its version

    if the feature is located inside a git repository,
    this will also print the git-rev and modified files
    '''

    import os
    import featuremonkey
    import importlib
    import subprocess

    def guess_version(feature_module):
        if hasattr(feature_module, '__version__'):
            return feature_module.__version__
        if hasattr(feature_module, 'get_version'):
            return feature_module.get_version()
        return ('unable to determine version:'
                ' please add __version__ or get_version()'
                ' to this feature module!')

    def git_rev(module):
        stdout, stderr = subprocess.Popen(
            ["git", "rev-parse", "HEAD"],
            cwd=os.path.dirname(module.__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()
        if 'Not a git repo' in stderr:
            return '-'
        else:
            return stdout.strip()

    def git_changes(module):
        stdout = subprocess.Popen(
            ["git", "diff", "--name-only"],
            cwd=os.path.dirname(module.__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()[0]
        return stdout.strip() or '-'

    if featurename in featuremonkey.get_features_from_equation_file(os.environ['PRODUCT_EQUATION_FILENAME']):
        print()
        print(featurename)
        print('-' * 60)
        print()
        is_subfeature = '.features.' in featurename
        try:
            feature_module = importlib.import_module(featurename)
        except ImportError:
            print('Error: unable to import feature "%s"' % featurename)

        print('Location: %s' % os.path.dirname(feature_module.__file__))
        print()
        if is_subfeature:
            print('Version: see parent feature')
            print()
        else:
            print('Version: %s' % str(guess_version(feature_module)))
            print()
            print('git: %s' % git_rev(feature_module))
            print()
            print('git changed: %s' % '\n\t\t'.join(git_changes(feature_module).split('\n')))
    else:
        print('No feature named ' + featurename)


def explain_features():
    '''print the location of each feature and its version

    if the feature is located inside a git repository, this will also print the git-rev and modified files
    '''
    from ape import tasks
    import featuremonkey
    import os

    featurenames = featuremonkey.get_features_from_equation_file(os.environ['PRODUCT_EQUATION_FILENAME'])

    for featurename in featurenames:
        tasks.explain_feature(featurename)


def selftest():
    '''run ape tests'''
    from ape import tests

    result = tests.run_all()
    if not result.wasSuccessful():
        raise Exception('Selftests failed! :(')
