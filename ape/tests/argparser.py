from __future__ import absolute_import
import unittest
import sys
from ape.main import get_task_parser, invoke_task
import sys
from .base import SilencedTest

class TestArgParser(SilencedTest, unittest.TestCase):

    def test_noparam(self):

        def noparam(): pass

        parser, proxy_args = get_task_parser(noparam)
        self.assertEquals(False, proxy_args)

        parsed_args = parser.parse_args(''.split())
        self.assertEquals({}, vars(parsed_args))
        self.assertRaises(SystemExit, parser.parse_args, 'arg1'.split())

    def test_proxy(self):

        def proxyparam(*args): pass

        parser, proxy_args = get_task_parser(proxyparam)
        self.assertEquals(True, proxy_args)

    def test_positional(self):

        def positionalparams(arg1, arg2): pass

        parser, proxy_args = get_task_parser(positionalparams)
        self.assertEquals(False, proxy_args)

        parsed_args = parser.parse_args('1 2'.split())
        self.assertEquals({'arg1': '1', 'arg2': '2'}, vars(parsed_args))
        self.assertRaises(SystemExit, parser.parse_args, '1'.split())

    def test_optional(self):

        def optionalparams(kw1='1', kw2='2'): pass

        parser, proxy_args = get_task_parser(optionalparams)
        self.assertEquals(False, proxy_args)

        parsed_args = parser.parse_args('--kw1 a --kw2 b'.split())
        self.assertEquals({'kw1': 'a', 'kw2': 'b'}, vars(parsed_args))

        parsed_args = parser.parse_args('--kw2 b'.split())
        self.assertEquals({'kw1': '1', 'kw2': 'b'}, vars(parsed_args))

        parsed_args = parser.parse_args(''.split())
        self.assertEquals({'kw1': '1', 'kw2': '2'}, vars(parsed_args))

        self.assertRaises(SystemExit, parser.parse_args, '1'.split())

    def test_positional_and_optional(self):

        def posoptparams(x, y, kw1='1', kw2='2'): pass

        parser, proxy_args = get_task_parser(posoptparams)
        self.assertEquals(False, proxy_args)

        parsed_args = parser.parse_args('f g --kw1 a --kw2 b'.split())
        self.assertEquals(
            {'x': 'f', 'y': 'g', 'kw1': 'a', 'kw2': 'b'},
            vars(parsed_args)
        )

        parsed_args = parser.parse_args('f g --kw2 b'.split())
        self.assertEquals(
            {'x': 'f', 'y': 'g', 'kw1': '1', 'kw2': 'b'},
            vars(parsed_args)
        )
        parsed_args = parser.parse_args('f g'.split())
        self.assertEquals(
            {'x': 'f', 'y': 'g', 'kw1': '1', 'kw2': '2'},
            vars(parsed_args)
        )

        self.assertRaises(SystemExit, parser.parse_args, '1'.split())
