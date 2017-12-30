# coding: utf-8
from __future__ import unicode_literals, print_function
from collections import defaultdict

import copy

from . import topsort, GraphCycleError
from . import detect_cycle

C_TYPES = (
    'first',
    'last',
    'before',
    'after'
)

FIRST = C_TYPES[0]
LAST = C_TYPES[1]
BEFORE = C_TYPES[2]
AFTER = C_TYPES[3]


class MultipleFirstConditionsError(Exception):
    def __init__(self, msg, occ1, occ2):
        super(MultipleFirstConditionsError, self).__init__(msg)
        self.occurences = [occ1, occ2]


class MultipleLastConditionsError(Exception):
    def __init__(self, msg, occ1, occ2):
        super(MultipleLastConditionsError, self).__init__(msg)
        self.occurences = [occ1, occ2]


class AfterConditionToLastError(Exception):
    pass


class OrderingCondition(object):
    name = None
    subject = None
    ctype = None

    def __init__(self, name, subject, ctype):
        if ctype not in C_TYPES:
            raise NotImplementedError('Selected ConditionType ({ctype}) is not available! Choose on of the available: {C_TYPES}'.format(
                ctype=ctype,
                C_TYPES=C_TYPES
            ))
        self.name = name
        self.subject = subject
        self.ctype = ctype


class OrderingConditions(object):
    def __init__(self, ordering_conditions=None):
        self.first = None
        self.last = None
        # self.before stores features as keys.
        # Each feature has a list of features which need to be loaded before the feature.
        self.before = defaultdict(list)
        if ordering_conditions:
            for condition in ordering_conditions:
                self.add_condition(condition)

    def add_condition(self, condition):
        ctype = condition.ctype
        if ctype == FIRST:
            if not self.first:
                self.first = condition.name
                self.before[self.first] = list()
            else:
                raise MultipleFirstConditionsError(
                    'Found multiple first conditions',
                    self.first,
                    condition
                )

        elif ctype == LAST:
            if not self.last:
                self.last = condition.name
                self.before[self.last] = list()
            else:
                raise MultipleLastConditionsError(
                    'Found multiple last conditions',
                    self.last,
                    condition
                )

        elif ctype == AFTER:
            if self.last and condition.subject == self.last:
                raise AfterConditionToLastError(
                    '\n After condition was applied to last condition: \n \t Condition: {condition} \n \t Last condition: {last}'.format(
                        last=self.last,
                        condition="{} {} {}".format(condition.name, condition.ctype, condition.subject)
                    )
                )
            else:
                # transform after to before by switching objects
                self.before[condition.name].append(condition.subject)


def _get_formatted_feature_dependencies(data):
    """
    Takes the format of the feature_order.json in featuremodel pool.
    Creates a list of conditions in the following format:
    ]
        dict(
            name='django_productline.features.admin',
            subject='django_productline',
            ctype='after'
        )
    ]
    :param data:
    :return: list
    """
    conditions = list()
    for k, v in data.items():
        for feature in v.get('after', list()):
            conditions.append(dict(
                name=k,
                subject=feature,
                ctype='after'
            ))
        if v.get('first', False):
            conditions.append(dict(
                name=k,
                subject=None,
                ctype='first'
            ))
        if v.get('last', False):
            conditions.append(dict(
                name=k,
                subject=None,
                ctype='last'
            ))
    return conditions


def _get_condition_instances(data):
    """
    Returns a list of OrderingCondition instances created from the passed data structure.
    The structure should be a list of dicts containing the necessary information:
    [
        dict(
            name='featureA',
            subject='featureB',
            ctype='after'
        ),
    ]
    Example says: featureA needs to be after featureB.
    :param data:
    :return:
    """
    conditions = list()
    for cond in data:
        conditions.append(OrderingCondition(
            name=cond.get('name'),
            subject=cond.get('subject'),
            ctype=cond.get('ctype')
        ))
    return conditions


class Feaquencer(object):
    def __init__(self, feature_selection, feature_dependencies):
        self.feature_set = set(feature_selection)
        self.feature_dependencies = feature_dependencies

    def arrange(self):
        self._init_graph()
        self._enrich_graph()
        self._validate_graph()

    def get_order(self):
        return self._get_total_order()

    def _init_graph(self):
        ordering_conditions = self._get_conditions()
        self.first = copy.deepcopy(ordering_conditions.first)
        self.last = copy.deepcopy(ordering_conditions.last)
        self.graph = copy.deepcopy(ordering_conditions.before)

    def _get_conditions(self):
        condition_list = _get_condition_instances(_get_formatted_feature_dependencies(self.feature_dependencies))
        return OrderingConditions(condition_list)

    def _enrich_graph(self):
        """
        Enrich the graph with the implicit conditions (first appears in every before-list,
        before-list of last should contain every feature, ...)
        :return:
        """
        self._add_missing_nodes()
        self._populate_befores()

    def _populate_befores(self):
        for feature in self.graph.keys():
            if self.first:
                if feature != self.first and feature not in set(self.graph[feature]):
                    self.graph[feature].append(self.first)
            if self.last:
                if feature != self.last and feature not in set(self.graph[self.last]):
                    self.graph[self.last].append(feature)

    def _add_missing_nodes(self):
        features_in_graph = set(self.graph.keys())
        for feature in self.feature_set:
            if feature not in features_in_graph:
                self.graph[feature] = list()

    def _validate_graph(self):
        cycle = detect_cycle(self.graph)
        if cycle:
            raise GraphCycleError(cycle)

    def _get_total_order(self):
        total_order_with_too_many_features = reversed(topsort(self.graph))
        total_order_with_selected_features = list()
        for feature in total_order_with_too_many_features:
            if feature in self.feature_set:
                total_order_with_selected_features.append(feature)
        return total_order_with_selected_features


def get_total_order(feature_selection, feature_dependencies):
    feaquencer = Feaquencer(feature_selection, feature_dependencies)
    feaquencer.arrange()
    return feaquencer.get_order()
