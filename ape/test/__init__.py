from __future__ import absolute_import
import unittest
from ape.test.argparser import TestArgParser
from ape.test.invokation import TestTaskInvokation
from ape.test.test_equation_generator import EquationGeneratorTests

def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestArgParser),
        unittest.TestLoader().loadTestsFromTestCase(TestTaskInvokation),
        unittest.TestLoader().loadTestsFromTestCase(EquationGeneratorTests),
    ])


def run_all():
    return unittest.TextTestRunner(verbosity=2).run(suite())
