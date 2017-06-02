from __future__ import absolute_import
import unittest
from ape.tests.argparser import TestArgParser
from ape.tests.invokation import TestTaskInvokation

# switch to the director and call python -m unittest discover tests


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestArgParser),
        unittest.TestLoader().loadTestsFromTestCase(TestTaskInvokation),
    ])


def run_all():
    return unittest.TextTestRunner(verbosity=2).run(suite())
