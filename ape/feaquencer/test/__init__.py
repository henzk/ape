from __future__ import absolute_import

import unittest

from feaquencer.test.test_cycledetect import *
from feaquencer.test.test_order_validation import *


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestCycleDetection),
        unittest.TestLoader().loadTestsFromTestCase(TestTopsort),
        unittest.TestLoader().loadTestsFromTestCase(OrderValidationTest),
    ])


def run_all():
    return unittest.TextTestRunner(verbosity=2).run(suite())
