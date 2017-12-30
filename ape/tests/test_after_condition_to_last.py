from __future__ import absolute_import, unicode_literals
import unittest

import copy

from ape.feaquencer import (
    get_total_order,
    AfterConditionToLastError
)

feature_selection_last_first = [
    'django_productline',
    'statics',
    'lessbuilder',
]

feature_selection_after_first = [
    'django_productline',
    'lessbuilder',
    'statics',
]

feature_dependencies_ok = {
    'django_productline': dict(
        first=True
    ),
    'statics': dict(
        last=True
    ),
    'lessbuilder': dict(
        after=['django_productline']
    )
}

feature_dependencies_false = {
    'django_productline': dict(
        first=True
    ),
    'lessbuilder': dict(
        after=['statics']
    ),
    'statics': dict(
        last=True
    )
}


class AfterConditionToLastTest(unittest.TestCase):
    def test_raises_last_first(self):
        fd = copy.deepcopy(feature_dependencies_false)
        self.assertRaises(AfterConditionToLastError, get_total_order, feature_selection_last_first, fd)

    def test_raises_after_first(self):
        fd = copy.deepcopy(feature_dependencies_false)
        self.assertRaises(AfterConditionToLastError, get_total_order, feature_selection_after_first, fd)

    def test_no_raise(self):
        fd = copy.deepcopy(feature_dependencies_ok)
        feature_order = get_total_order(feature_selection_last_first, fd)
        self.assertTrue(feature_order[0] == 'django_productline')
        self.assertTrue(feature_order[1] == 'lessbuilder')
        self.assertTrue(feature_order[2] == 'statics')
