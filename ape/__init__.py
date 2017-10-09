from __future__ import print_function, unicode_literals
import featuremonkey
import inspect
import sys
from .exceptions import InvalidAccess, InvalidTask, TaskAlreadyRegistered, TaskNotFound, FeatureNotFound, EnvironmentIncomplete

__version__ = '0.4.0'
__author__ = 'Hendrik Speidel <hendrik@schnapptack.de>'
SHORT_HEADER = '''ape - a productive environment

'''


def _get_invalid_accessor(func_name):

    def invalid_accessor(*args, **kws):
        raise InvalidAccess(
            'task "%s" needs to be accessed as "ape.tasks.%s"!' % (
                func_name, func_name
            )
        )

    return invalid_accessor


def get_signature(name, func):
    """
    Helper to generate a readable signature for a function
    :param name:
    :param func:
    :return:
    """
    args, varargs, keywords, defaults = inspect.getargspec(func)
    defaults = defaults or []
    posargslen = len(args) - len(defaults)
    if varargs is None and keywords is None:
        sig = name + '('
        sigargs = []
        for idx, arg in enumerate(args):
            if idx < posargslen:
                sigargs.append(arg)
            else:
                default = repr(defaults[idx - posargslen])
                sigargs.append(arg + '=' + default)
        sig += ', '.join(sigargs) + ')'
        return sig
    elif not args and varargs and not keywords and not defaults:
        return name + '(*' + varargs + ')'
    else:
        raise InvalidTask('ape tasks may not use **kwargs')


class TerminalColor:
    """
    Defines available terminal colors.
    """
    colors = dict(
        RESET="\033[0;0m",
        RED="\033[1;31m",
        BLUE="\033[1;34m",
        CYAN="\033[1;36m",
        GREEN="\033[0;32m",
    )

    @classmethod
    def set(cls, color):
        """
        Sets the terminal to the passed color.
        :param color: one of the availabe colors.
        """
        sys.stdout.write(cls.colors.get(color, cls.colors['RESET']))

    @classmethod
    def reset(cls):
        """
        Rsets the terminal color.
        :return:
        """
        sys.stdout.write(cls.colors['RESET'])


class Tasks(object):
    """
    Ape tasks registry.
    """

    def __init__(self):
        # import the module that tasks live in
        from . import _tasks
        self._tasks = _tasks
        self._helper_names = set()

    def register(self, func):
        """
        Register a task. Typically used as a decorator to the task function.

        If a task by that name already exists,
        a TaskAlreadyRegistered exception is raised.
        :param func:
        :return:
        """

        if hasattr(self._tasks, func.__name__):
            raise TaskAlreadyRegistered(func.__name__)
        setattr(self._tasks, func.__name__, func)
        return _get_invalid_accessor(func.__name__)

    def register_helper(self, func):
        """
        A helper is a task that is not directly exposed to
        the command line
        :param func:
        :return:
        """

        self._helper_names.add(func.__name__)
        return self.register(func)

    def get_tasks(self):
        """
        Return tasks as list of (name, function) tuples.
        """

        def predicate(item):
            return (inspect.isfunction(item) and
                    item.__name__ not in self._helper_names)
        return inspect.getmembers(self._tasks, predicate)

    def get_task(self, name, include_helpers=True):
        """
        Get task identified by name or raise TaskNotFound if there
        is no such task
        :param name:
        :param include_helpers:
        :return:
        """

        if not include_helpers and name in self._helper_names:
            raise TaskNotFound(name)
        try:
            return getattr(self._tasks, name)
        except AttributeError:
            raise TaskNotFound(name)

    def print_task_help(self, task, name):
        """
        Prints the help for the passed task with the passed name.
        :param task: the task function object
        :param name: the name of the module.
        """
        TerminalColor.set('GREEN')
        print(get_signature(name, task))

        # TODO: print the location does not work properly and sometimes returns None
        # print('    => defined in: {}'.format(inspect.getsourcefile(task)))
        help_msg = inspect.getdoc(task) or ''
        TerminalColor.reset()
        print('   ' + help_msg.replace('\n', '\n   '))
        TerminalColor.reset()
        print()

    def help(self, taskname=None):
        """
        List tasks or provide help for specific task
        :param taskname:
        :return:
        """

        if not taskname:
            print(inspect.getdoc(self._tasks))
            print()
            print('Available tasks:')
            print()

            for task in self.get_tasks():
                self.print_task_help(task[1], task[0])
        else:
            try:
                task = self.get_task(taskname)
                self.print_task_help(task, task.__name__)

            except TaskNotFound:
                print('Task "%s" not found! Use "ape help" to get usage information.' % taskname)

    def __getattr__(self, name):
        """
        Simple proxy to tasks module
        tasks have to be accessed using only this method,
        e.g. ape.tasks.foo() to call the foo task.
        :param name:
        :return:
        """

        return self.get_task(name)

    def superimpose(self, module):
        """
        superimpose a task module on registered tasks'''
        :param module:
        :return:
        """
        featuremonkey.compose(module, self._tasks)
        self._tasks.FEATURE_SELECTION.append(module.__name__)


tasks = Tasks()
