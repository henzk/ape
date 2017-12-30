from __future__ import absolute_import
import unittest

from ape.tests.test_after_condition_to_last import AfterConditionToLastTest
from ape.tests.test_argparser import TestArgParser
from ape.tests.test_invokation import TestTaskInvokation
from ape.tests.test_extract_feature_order import ExtractFeatureOrderTestCase
from ape.tests.test_feature_order_validator import FeatureOrderValidatorTestCase
from ape.tests.test_cycledetect import TestCycleDetection, TestTopsort
from ape.tests.test_order_validation import OrderValidationTest


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestArgParser),
        unittest.TestLoader().loadTestsFromTestCase(TestTaskInvokation),
        unittest.TestLoader().loadTestsFromTestCase(ExtractFeatureOrderTestCase),
        unittest.TestLoader().loadTestsFromTestCase(FeatureOrderValidatorTestCase),
        unittest.TestLoader().loadTestsFromTestCase(TestCycleDetection),
        unittest.TestLoader().loadTestsFromTestCase(TestTopsort),
        unittest.TestLoader().loadTestsFromTestCase(OrderValidationTest),
        unittest.TestLoader().loadTestsFromTestCase(AfterConditionToLastTest),
    ])


def run_all():
    return unittest.TextTestRunner(verbosity=2).run(suite())
