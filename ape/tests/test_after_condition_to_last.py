from __future__ import absolute_import, unicode_literals
import unittest

import copy
from ape.feaquencer import (
    get_total_order,
    AfterConditionToLastError
)

feature_selection = [
    'django_productline',
    'schnadmin2',
    'statics'
]

feature_dependencies_ok = {
    'django_productline': dict(
        first=True
    ),
    'statics': dict(
        last=True
    ),
    'schnadmin2': dict(
        after=['django_productline']
    )
}

feature_dependencies_false = {
    'django_productline': dict(
        first=True
    ),
    'statics': dict(
        last=True
    ),
    'schnadmin2': dict(
        after=['statics']
    )
}


class AfterConditionToLastTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_raises_if_condition_true(self):
        fd = copy.deepcopy(feature_dependencies_false)
        self.assertRaises(AfterConditionToLastError, get_total_order, feature_selection, fd)

    def test_no_raise_if_condition_false(self):
        fd = copy.deepcopy(feature_dependencies_ok)
        feature_order = get_total_order(feature_selection, fd)
        self.assertTrue(feature_order[0] == 'django_productline')
        self.assertTrue(feature_order[1] == 'schnadmin2')
        self.assertTrue(feature_order[2] == 'statics')
