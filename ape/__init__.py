import featuremonkey
import inspect
from functools import wraps

__version__ = '0.1'
__author__ = 'Hendrik Speidel <hendrik@schnapptack.de>'
SHORT_HEADER = '''ape - a productive environment

'''

class EnvironmentIncomplete(Exception): pass

class FeatureNotFound(Exception): pass

class TaskNotFound(Exception): pass

class TaskAlreadyRegistered(Exception): pass


def get_signature(name, func):
    '''helper to generate a readable signature for a function'''
    args, varargs, keywords, defaults = inspect.getargspec(func)
    defaults = defaults or []
    if varargs is None and keywords is None:
        sig = name + '('
        sigargs = []
        for idx, arg in enumerate(args):
            if idx < len(args) - len(defaults):
                sigargs.append(arg)
            else:
                default = repr(defaults[idx - len(defaults)])
                sigargs.append(arg + '=' + default)
        sig += ', '.join(sigargs) + ')'
        return sig
    elif not args and varargs and not keywords and not defaults:
        return name + '(*' + varargs + ')'
    else:
        raise


class Tasks(object):
    '''
    ape tasks registry
    '''

    def __init__(self):
        #import the module that tasks live in
        from . import _tasks
        self._tasks = _tasks

    def register(self, func):
        '''register a task - 
        typically used as a decorator to the task function.
        
        If a task by that name already exists,
        a TaskAlreadyRegistered exception is raised.
        '''
        if hasattr(self._tasks, func.__name__):
            raise TaskAlreadyRegistered(func.__name__)
        setattr(self._tasks, func.__name__, func)

    def get_tasks(self):
        '''
        return tasks as list of (name, function) tuples
        '''
        return inspect.getmembers(self._tasks, inspect.isfunction)

    def get_task(self, name):
        '''get task identified by name or raise TaskNotFound if there
        is no such task
        '''
        try:
            return getattr(self._tasks, name)
        except AttributeError:
            raise TaskNotFound(name)

    def help(self, taskname=None):
        '''list tasks or provide help for specific task'''
        if not taskname:
            print inspect.getdoc(self._tasks)
            print
            print 'Available tasks:'
            print
            for task in self.get_tasks():
                print '  ' + get_signature(*task)
                help_msg = inspect.getdoc(task[1]) or ''
                help_msg = help_msg.split('\n')[0]
                print '    ' + help_msg
                print
        else:
            try:
                task = self.get_task(taskname)
                print SHORT_HEADER
                print get_signature(task.__name__, task)
                print
                print inspect.getdoc(task)
                print
                print 'defined in: ' + inspect.getfile(task)
            except TaskNotFound:
                print 'Task "%s" not found! Use "ape help" to get usage information.' % taskname

    def __getattr__(self, name):
        '''simple proxy to tasks module
        tasks have to be accessed using only this method,
        e.g. ape.tasks.foo() to call the foo task.
        '''
        return self.get_task(name)

    def superimpose(self, module):
        '''superimpose a task module on registered tasks'''
        featuremonkey.compose(module, self._tasks)

tasks = Tasks()
