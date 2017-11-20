from __future__ import absolute_import, unicode_literals
from ape.feaquencer import detect_cycle, topsort
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestCycleDetection(unittest.TestCase):

    def test_empty_graph(self):
        self.assertIsNone(detect_cycle(dict()))

    def test_single_node(self):
        self.assertIsNone(detect_cycle(dict(a=[])))

    def test_two_nodes(self):
        self.assertIsNone(detect_cycle(OrderedDict(a=[], b=[])))

    def test_single_node_reflexive_vertex(self):
        self.assertEqual(['a', 'a'], detect_cycle(dict(a=['a'])))

    def test_two_nodes_cycle(self):
        self.assertEqual(
            ['a', 'b', 'a'],
            detect_cycle(
                OrderedDict([
                    ('a', ['b']),
                    ('b', ['a'])
                ])
            )
        )

    def test_two_nodes_cycle_r(self):
        self.assertEqual(
            ['b', 'a', 'b'],
            detect_cycle(
                OrderedDict([
                    ('b', ['a']),
                    ('a', ['b'])
                ])
            )
        )

    def test_two_paths(self):
        self.assertIsNone(
            detect_cycle(
                OrderedDict([
                    ('a', ['b', 'c']),
                    ('b', ['c']),
                    ('c', []),
                    ('d', ['b'])
                ])
            )
        )


class TestTopsort(unittest.TestCase):
    def setUp(self):
        pass

    def test_empty_graph(self):
        self.assertEqual(
            [],
            topsort(dict())
        )

    def test_single_node(self):
        self.assertEqual(
            ['a'],
            topsort(dict(a=[]))
        )

    def test_two_nodes(self):
        self.assertEqual(
            ['a', 'b'],
            topsort(dict(a=['b'], b=[]))
        )

    def test_three_nodes(self):
        self.assertEqual(
            ['a', 'b', 'c'],
            topsort(dict(a=['b'], b=['c'], c=[]))
        )

    def test_forest(self):
        self.assertEqual(
            ['a', 'b', 'c', 'd'],
            topsort(OrderedDict([
                ('d', []),
                ('b', ['c']),
                ('c', []),
                ('a', ['b']),
            ]))
        )
