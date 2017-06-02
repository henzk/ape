# coding: utf-8
from __future__ import unicode_literals, print_function
import unittest
from ape.container_mode import utils
import os.path

__all__ = ['ExtractFeatureOrderTestCase']


class ExtractFeatureOrderTestCase(unittest.TestCase):
    """
    Test the extract feature order helper.
    """


    def test_smoke_test(self):

        model_xml_path = os.path.join(
            os.path.dirname(__file__), '_data/model.xml'
        )

        feature_order = utils.extract_feature_order_from_model_xml(model_xml_path)
        self.assertEqual(
            feature_order,
            ['a', 'b', 'c', 'd', 'e']
        )
