import featuremonkey
import inspect
from functools import wraps

__version__ = '0.3.0'
__author__ = 'Hendrik Speidel <hendrik@schnapptack.de>'
SHORT_HEADER = '''ape - a productive environment

'''

class EnvironmentIncomplete(Exception): pass

class FeatureNotFound(Exception): pass

class TaskNotFound(Exception): pass

class TaskAlreadyRegistered(Exception): pass

class InvalidAccess(Exception): pass

class InvalidTask(Exception): pass

def _get_invalid_accessor(func_name):

    def invalid_accessor(*args, **kws):
        raise InvalidAccess(
            'task "%s" needs to be accessed as "ape.tasks.%s"!' % (
                func_name, func_name
            )
        )

    return invalid_accessor

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
        raise InvalidTask('ape tasks may not use **kwargs')


class Tasks(object):
    '''
    ape tasks registry
    '''

    def __init__(self):
        #import the module that tasks live in
        from . import _tasks
        self._tasks = _tasks
        self._helper_names = set()

    def register(self, func):
        '''register a task - 
        typically used as a decorator to the task function.
        
        If a task by that name already exists,
        a TaskAlreadyRegistered exception is raised.
        '''
        if hasattr(self._tasks, func.__name__):
            raise TaskAlreadyRegistered(func.__name__)
        setattr(self._tasks, func.__name__, func)
        return _get_invalid_accessor(func.__name__)

    def register_helper(self, func):
        '''a helper is a task that is not directly exposed to
        the command line
        '''
        self._helper_names.add(func.__name__)
        return self.register(func)

    def get_tasks(self):
        '''
        return tasks as list of (name, function) tuples
        '''
        def predicate(item):
            return (inspect.isfunction(item) and 
                item.__name__ not in self._helper_names
            )
        return inspect.getmembers(self._tasks, predicate)

    def get_task(self, name, include_helpers=True):
        '''get task identified by name or raise TaskNotFound if there
        is no such task
        '''
        if not include_helpers and name in self._helper_names:
            raise TaskNotFound(name)
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
                print
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
        self._tasks.FEATURE_SELECTION.append(module.__name__)

tasks = Tasks()
