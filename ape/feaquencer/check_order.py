# coding: utf-8
from __future__ import unicode_literals, print_function
from collections import defaultdict

import copy

from . import topsort
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
    def __init__(self):
        self.first = None
        self.last = None
        # self.before stores features as keys.
        # Each feature has a list of features which need to be loaded before the feature.
        self.before = defaultdict(list)

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


def get_total_order(feature_selection, feature_dependencies):
    feature_set = set(feature_selection)
    condition_list = _get_condition_instances(_get_formatted_feature_dependencies(feature_dependencies))
    oc = OrderingConditions()
    for condition in condition_list:
        oc.add_condition(condition)
    first = copy.deepcopy(oc.first)
    last = copy.deepcopy(oc.last)
    graph = copy.deepcopy(oc.before)
    for feature in feature_selection:
        if feature not in graph.keys():
            graph[feature] = list()
    for feature in graph.keys():
        if first:
            if feature != first:
                graph[feature].append(first)
        if last:
            if feature != last:
                graph[last].append(feature)
    if not detect_cycle(graph):
        total_order_with_too_many_features = reversed(topsort(graph))
        total_order_with_selected_features = list()
        for feature in total_order_with_too_many_features:
            if feature in feature_set:
                total_order_with_selected_features.append(feature)
        return total_order_with_selected_features
