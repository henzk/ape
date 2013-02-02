from __future__ import absolute_import
import unittest
from ape.test.argparser import TestArgParser
from ape.test.invokation import TestTaskInvokation

def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestArgParser),
        unittest.TestLoader().loadTestsFromTestCase(TestTaskInvokation),
    ])


def run_all():
    return unittest.TextTestRunner(verbosity=2).run(suite())
