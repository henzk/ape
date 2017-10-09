# coding: utf-8
from __future__ import unicode_literals, print_function
import unittest
from ape.container_mode import validators

__all__ = ['FeatureOrderValidatorTestCase']


class FeatureOrderValidatorTestCase(unittest.TestCase):
    def test_smoke_test(self):
        feature_list = [
            'schnapache',
            'feature_sendfile',
            'feature_sendfile_xsendfile'
        ]

        constraints = dict(
            schnapache=dict(),
            feature_sendfile=dict(after=['schnapache']),
            feature_sendfile_xsendfile=dict(after=['feature_sendfile']),
        )

        validator = validators.FeatureOrderValidator(feature_list, constraints)
        validator.check_order()

    def test_before_violation(self):
        feature_list = [
            'schnapache',
            'feature_sendfile_xsendfile',
            'feature_sendfile',
        ]

        constraints = dict(
            schnapache=dict(),
            feature_sendfile=dict(after=['schnapache']),
            feature_sendfile_xsendfile=dict(after=['feature_sendfile']),
        )

        validator = validators.FeatureOrderValidator(feature_list, constraints)
        validator.check_order()

        self.assertTrue(validator.has_errors())
        self.assertEqual(len(validator.get_violations()), 1)

    def test_before_violation2(self):
        constraints = dict(
            a=dict(is_first=True, after=[], before=['b', 'c', 'd', 'e']),
            b=dict(after=['a'], before=['c', 'd', 'e']),
            c=dict(after=['a', 'b'], before=['d', 'e']),
            d=dict(after=['a', 'b', 'c'], before=['e']),
            e=dict(after=['a', 'b', 'c', 'd'], before=[]),
        )

        validator = validators.FeatureOrderValidator(['a', 'b', 'c', 'd', 'e'], constraints)
        validator.check_order()
        self.assertFalse(validator.has_errors())

        validator = validators.FeatureOrderValidator(['b', 'a', 'c', 'd', 'e'], constraints)
        validator.check_order()
        self.assertTrue(validator.has_errors())
        self.assertEqual(len(validator.get_violations()), 2)

        validator = validators.FeatureOrderValidator(['e', 'd', 'c', 'b', 'a'], constraints)
        validator.check_order()
        self.assertTrue(validator.has_errors())
        self.assertEqual(len(validator.get_violations()), 20)

    def test_pos(self):
        constraints = dict(
            a=dict(position=0),
            b=dict(position=1),
            c=dict(position=2),
            d=dict(position=0),
            e=dict(position=4),
        )
        validator = validators.FeatureOrderValidator(['a', 'b', 'c', 'd', 'e'], constraints)
        validator.check_order()
        self.assertTrue(validator.has_errors())
        self.assertEqual(len(validator.get_violations()), 1)
