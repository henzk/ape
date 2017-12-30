from __future__ import print_function, unicode_literals
import argparse
import inspect
import importlib
import sys
import os
import traceback
from featuremonkey import get_features_from_equation_file
from ape.exceptions import TaskNotFound, FeatureNotFound, EnvironmentIncomplete, InvalidTask
from ape import tasks


ERRMSG_UNSUPPORTED_SIG = '''Task "%s" has an unsupported signature.
Supported signatures are:
    - *args only
    - combination of explicit positional and explicit keyword args
    - **kws are NOT supported
'''


def get_task_parser(task):
    """
    Construct an ArgumentParser for the given task.

    This function returns a tuple (parser, proxy_args).
    If task accepts varargs only, proxy_args is True.
    If task accepts only positional and explicit keyword args,
    proxy args is False.
    """
    args, varargs, keywords, defaults = inspect.getargspec(task)
    defaults = defaults or []
    parser = argparse.ArgumentParser(
        prog='ape ' + task.__name__,
        add_help=False,
        description=task.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    posargslen = len(args) - len(defaults)
    if varargs is None and keywords is None:
        for idx, arg in enumerate(args):
            if idx < posargslen:
                parser.add_argument(arg)
            else:
                default = defaults[idx - posargslen]
                parser.add_argument('--' + arg, default=default)
        return parser, False
    elif not args and varargs and not keywords and not defaults:
        return parser, True
    else:
        raise InvalidTask(ERRMSG_UNSUPPORTED_SIG % task.__name__)


def invoke_task(task, args):
    """
    Parse args and invoke task function.

    :param task: task function to invoke
    :param args: arguments to the task (list of str)
    :return: result of task function
    :rtype: object
    """
    parser, proxy_args = get_task_parser(task)
    if proxy_args:
        return task(*args)
    else:
        pargs = parser.parse_args(args)
        return task(**vars(pargs))


def get_task_module(feature):
    """
    Return imported task module of feature.

    This function first tries to import the feature and raises FeatureNotFound
    if that is not possible.
    Thereafter, it looks for a submodules called ``apetasks`` and ``tasks`` in that order.
    If such a submodule exists, it is imported and returned.

    :param feature: name of feature to fet task module for.
    :raises: FeatureNotFound if feature_module could not be imported.
    :return: imported module containing the ape tasks of feature or None,
                if module cannot be imported.
    """
    try:
        importlib.import_module(feature)
    except ImportError:
        raise FeatureNotFound(feature)

    tasks_module = None

    # ape tasks may be located in a module called apetasks
    # or (if no apetasks module exists) in a module called tasks
    try:
        tasks_module = importlib.import_module(feature + '.apetasks')
    except ImportError:
        # No apetasks module in feature ... try tasks
        pass

    try:
        tasks_module = importlib.import_module(feature + '.tasks')
    except ImportError:
        # No tasks module in feature ... skip it
        pass

    return tasks_module


def run(args, features=None):
    """
    Run an ape task.

    Composes task modules out of the selected features and calls the
    task with arguments.

    :param args: list comprised of task name followed by arguments
    :param features: list of features to compose before invoking the task
    """
    features = features or []
    for feature in features:
        tasks_module = get_task_module(feature)
        if tasks_module:
            tasks.superimpose(tasks_module)

    if len(args) < 2 or (len(args) == 2 and args[1] == 'help'):
        tasks.help()
    else:
        taskname = args[1]
        try:
            task = tasks.get_task(taskname, include_helpers=False)
        except TaskNotFound:
            print('Task "%s" not found! Use "ape help" to get usage information.' % taskname)
        else:
            remaining_args = args[2:] if len(args) > 2 else []
            invoke_task(task, remaining_args)


def main():
    """
    Entry point when used via command line.

    Features are given using the environment variable ``PRODUCT_EQUATION``.
    If it is not set, ``PRODUCT_EQUATION_FILENAME`` is tried: if it points
    to an existing equation file that selection is used.

    (if ``APE_PREPEND_FEATURES`` is given, those features are prepended)

    If the list of features is empty, ``ape.EnvironmentIncomplete`` is raised.
    """
    # check APE_PREPEND_FEATURES
    features = os.environ.get('APE_PREPEND_FEATURES', '').split()
    # features can be specified inline in PRODUCT_EQUATION
    inline_features = os.environ.get('PRODUCT_EQUATION', '').split()
    if inline_features:
        # append inline features
        features += inline_features
    else:
        # fallback: features are specified in equation file
        feature_file = os.environ.get('PRODUCT_EQUATION_FILENAME', '')
        if feature_file:
            # append features from equation file
            features += get_features_from_equation_file(feature_file)
        else:
            if not features:
                raise EnvironmentIncomplete(
                    'Error running ape:\n'
                    'Either the PRODUCT_EQUATION or '
                    'PRODUCT_EQUATION_FILENAME environment '
                    'variable needs to be set!'
                )

    # run ape with features selected
    run(sys.argv, features=features)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
