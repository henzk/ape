from __future__ import absolute_import, unicode_literals
import unittest

import copy
from ape.feaquencer import (
    get_total_order,
    MultipleFirstConditionsError,
    MultipleLastConditionsError,
    GraphCycleError
)

# Randomly ordered feature selection
feature_selection = [
    'django_productline',
    'schnadmin2',
    'styler',
    'django_productline.features.djpladmin',
    'schnadmin2_sidenav',
    'django_productline.features.development',
    'lessbuilder',
    'statics'
]

feature_dependencies = {
    'django_productline.features.staticfiles': dict(
        after=['django_productline']
    ),
    'django_productline': dict(
        first=True
    ),
    'schnadmin2': dict(
        after=['lessbuilder', 'django_productline.features.djpladmin']
    ),
    'schnadmin2_sidenav': dict(
        after=['schnadmin2']
    ),
    'django_productline.features.development': dict(
        last=True
    ),
    'lessbuilder': dict(
        after=['styler']
    ),
    'statics': dict(
        after=['lessbuilder']
    )
}


class OrderValidationTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_check_for_multiple_first(self):
        fd = copy.deepcopy(feature_dependencies)
        fd['lessbuilder']['first'] = True
        self.assertRaises(MultipleFirstConditionsError, get_total_order, feature_selection, fd)

    def test_check_for_multiple_last(self):
        fd = copy.deepcopy(feature_dependencies)
        fd['lessbuilder']['last'] = True
        self.assertRaises(MultipleLastConditionsError, get_total_order, feature_selection, fd)

    def test_check_django_productline_order(self):
        fd = copy.deepcopy(feature_dependencies)
        order = get_total_order(feature_selection, fd)
        self.assertTrue(order.index('django_productline') == 0)

    def test_check_styler_order(self):
        fd = copy.deepcopy(feature_dependencies)
        order = get_total_order(feature_selection, fd)
        self.assertTrue(order.index('styler') >= 1)

    def test_check_lessbuilder_order(self):
        fd = copy.deepcopy(feature_dependencies)
        order = get_total_order(feature_selection, fd)
        self.assertTrue(order.index('styler') < order.index('lessbuilder'))

    def test_check_development_order(self):
        fd = copy.deepcopy(feature_dependencies)
        order = get_total_order(feature_selection, fd)
        self.assertTrue(order.index('django_productline.features.development') == len(order) - 1)

    def test_raise_graph_cycle_error(self):
        fd = copy.deepcopy(feature_dependencies)
        # create cycle:
        #        before         before
        #  statics => lessbuilder => statics
        fd['lessbuilder']['after'] = ['statics']
        self.assertRaises(GraphCycleError, get_total_order, feature_selection, fd)
