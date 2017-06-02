from __future__ import absolute_import
import unittest
import sys
from ape.main import get_task_parser, invoke_task
import sys
from .base import SilencedTest

class InvalidParam(object): pass

class Params(object):
    def __init__(self):
        self._data = dict()

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            return InvalidParam()

    def __setattr__(self, name, value):
        if name == '_data':
            super(Params, self).__setattr__(name, value)
        else:
            self._data[name] = value

class TestTaskInvokation(SilencedTest, unittest.TestCase):

    def test_noparam(self):

        params = Params()
        def noparam():
            params.called = True

        invoke_task(noparam, ''.split())
        self.assertTrue(params.called)

        self.assertRaises(SystemExit, invoke_task, noparam, 'arg'.split())

    def test_proxy(self):

        params = Params()
        def proxyparam(*args):
            params.args = args

        invoke_task(proxyparam, ''.split())
        self.assertEqual((), params.args)

        testargs = tuple('a b c d --e --f --g'.split())
        invoke_task(proxyparam, testargs)
        self.assertEqual(testargs, params.args)

    def test_positional(self):

        params = Params()
        def positionalparams(arg1, arg2):
            params.args = (arg1, arg2)

        testargs = tuple('aa bb'.split())
        invoke_task(positionalparams, testargs)
        self.assertEqual(testargs, params.args)

        self.assertRaises(SystemExit, invoke_task,
            positionalparams, 'arg1only'.split()
        )
        self.assertRaises(SystemExit, invoke_task,
            positionalparams, 'arg1 arg2 1argtoomany'.split()
        )

    def test_optional(self):

        params = Params()
        def optionalparams(kw1='1', kw2='2'):
            params.kws = (kw1, kw2)

        testargs = tuple('--kw1 aa --kw2 bb'.split())
        invoke_task(optionalparams, testargs)
        self.assertEqual(('aa', 'bb'), params.kws)

        testargs = tuple('--kw1 aa'.split())
        invoke_task(optionalparams, testargs)
        self.assertEqual(('aa', '2'), params.kws)

        testargs = tuple(''.split())
        invoke_task(optionalparams, testargs)
        self.assertEqual(('1', '2'), params.kws)

        self.assertRaises(SystemExit, invoke_task,
            optionalparams, 'posarg --kw1 aa'.split()
        )
        self.assertRaises(SystemExit, invoke_task,
            optionalparams, 'posarg1 posarg2'.split()
        )

    def test_positional_and_optional(self):

        params = Params()
        def posoptparams(x, y, kw1='1', kw2='2'):
            params.args = (x, y)
            params.kws = (kw1, kw2)

        testargs = tuple('a b --kw2 bb --kw1 aa'.split())
        invoke_task(posoptparams, testargs)
        self.assertEqual(('a', 'b'), params.args)
        self.assertEqual(('aa', 'bb'), params.kws)

        testargs = tuple('a b --kw1 aa'.split())
        invoke_task(posoptparams, testargs)
        self.assertEqual(('a', 'b'), params.args)
        self.assertEqual(('aa', '2'), params.kws)

        testargs = tuple('a b'.split())
        invoke_task(posoptparams, testargs)
        self.assertEqual(('a', 'b'), params.args)
        self.assertEqual(('1', '2'), params.kws)

        self.assertRaises(SystemExit, invoke_task,
            posoptparams, 'posarg --kw1 aa'.split()
        )
        self.assertRaises(SystemExit, invoke_task,
            posoptparams, 'posarg1 posarg2 posarg3'.split()
        )
