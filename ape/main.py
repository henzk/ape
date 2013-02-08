import argparse
import inspect
import importlib
import sys
import os
from ape import tasks, TaskNotFound, FeatureNotFound, EnvironmentIncomplete
from featuremonkey import get_features_from_equation_file

def get_task_parser(task):
    '''
    construct an ArgumentParser for task
    this function returns a tuple (parser, proxy_args)
    if task accepts varargs only, proxy_args is True.
    if task accepts only positional and explicit keyword args, 
    proxy args is False.
    '''

    args, varargs, keywords, defaults = inspect.getargspec(task)
    defaults = defaults or []
    parser = argparse.ArgumentParser(
        prog='ape ' + task.__name__,
        add_help=False,
        description = task.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    if varargs is None and keywords is None:
        for idx, arg in enumerate(args):
            if idx < len(args) - len(defaults):
                parser.add_argument(arg)
            else:
                default = defaults[idx - len(defaults)]
                parser.add_argument('--' + arg, default=default)
        return parser, False
    elif not args and varargs and not keywords and not defaults:
        return parser, True
    else:
        raise

def invoke_task(task, args):
    '''
    invoke task with args
    '''
    parser, proxy_args = get_task_parser(task)
    if proxy_args:
        task(*args)
    else:
        pargs = parser.parse_args(args)
        task(**vars(pargs))

def run(args, features=None):
    '''
    composes task modules of the selected features and calls the
    task given by args
    '''

    features = features or []
    for feature in features:
        try:
            feature_module = importlib.import_module(feature)
        except ImportError:
            raise FeatureNotFound(feature)
        try:
            tasks_module = importlib.import_module(feature + '.tasks')
            tasks.superimpose(tasks_module)
        except ImportError:
            #No tasks module in feature ... skip it
            pass

    if len(args) < 2 or (len(args) == 2 and args[1] == 'help'):
        tasks.help()
    else:
        taskname = args[1]
        try:
            task = tasks.get_task(taskname, include_helpers=False)
        except TaskNotFound:
            print 'Task "%s" not found! Use "ape help" to get usage information.' % taskname
        else:
            remaining_args = args[2:] if len(args) > 2 else []
            invoke_task(task, remaining_args)

def main():
    '''
    entry point when used via command line
    
    features are given using the environment variable PRODUCT_EQUATION.
    If it is not set, PRODUCT_EQUATION_FILENAME is tried: if it points
    to an existing equation file that selection is used.
    If that fails ``ape.EnvironmentIncomplete`` is raised.
    '''

    #check APE_PREPEND_FEATURES
    features = os.environ.get('APE_PREPEND_FEATURES', '').split()
    #features can be specified inline in PRODUCT_EQUATION
    inline_features = os.environ.get('PRODUCT_EQUATION', '').split()
    if inline_features:
        #append inline features
        features += inline_features
    else:
        #fallback: features are specified in equation file
        feature_file = os.environ.get('PRODUCT_EQUATION_FILENAME', '')
        if feature_file:
            #append features from equation file
            features += get_features_from_equation_file(feature_file)
        else:
            if not features:
                print (
                    'Error running ape:\n'
                    'Either the PRODUCT_EQUATION or '
                    'PRODUCT_EQUATION_FILENAME environment '
                    'variable needs to be set!'
                )
                sys.exit(1)

    #run ape with features selected
    run(sys.argv, features=features)

if __name__ == '__main__':
    main()
