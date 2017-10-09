from __future__ import print_function, unicode_literals
import operator

__all__ = ['FeatureOrderValidator', ]


class FeatureOrderValidator(object):
    """
    This class provides an API to validate the correct order of the given list of feature names
    and the passed constraints.
    """

    def __init__(self, feature_list, constraints):
        """
        Constructor;
        :param feature_list: list of feature names
        :param constraints: dict(<featurename>=dict(before=[], after=[]))
        :return:
        """
        # replace potential __ syntax with dots (may come from model.xml)
        self.feature_list = [fn.replace('__', '.') for fn in feature_list]
        self.constraints = constraints
        self.violations = []

    def check_order(self):
        """
        Performs the check and store the violations in self.violations.
        :return: boolean indicating the error state
        """

        for feature, info in self.constraints.items():
            self._check_feature(feature, info, 'before')
            self._check_feature(feature, info, 'after')
            self._check_position(feature, info)

        return not self.has_errors()

    def _check_feature(self, feature, info, mode):
        """
        Private helper method performing the order check.
        :param feature: the feature to check.
        :param info: the info dict containing the before and after constraints
        :param mode: after | before string
        :return: None
        """

        op = dict(
            before=operator.gt,
            after=operator.lt
        )[mode]

        feature_pos = self.get_feature_position(feature)

        if feature_pos is not None:
            # only proceed if the the feature exists in the current feature list

            for other in info.get(mode, []):
                other_pos = self.get_feature_position(other)

                if other_pos is not None:
                    # only proceed if the the other feature exists in the current feature list
                    if op(feature_pos, other_pos):
                        message = '{feature} (pos {feature_pos}) must be {mode} feature {other} (pos {other_pos}) but isn\'t.'.format(
                            feature=feature,
                            feature_pos=feature_pos,
                            other=other,
                            other_pos=other_pos,
                            mode=mode.upper()
                        )
                        self.violations.append((feature, message))

    def _check_position(self, feature, info):
        """
        Takes the featur and the info dict and checks for the forced position
        :param feature:
        :param info:
        :return:
        """
        pos = info.get('position')
        if pos is not None:
            feature_pos = self.get_feature_position(feature)
            if feature_pos is not None:
                if feature_pos != pos:
                    message = '{feature} has a forced position on ({pos}) but is on position {feature_pos}.'.format(
                        feature=feature,
                        pos=pos,
                        feature_pos=feature_pos
                    )
                    self.violations.append((feature, message))

    def get_feature_position(self, feature):
        """
        Take the name of a feature and returns the position of that feature in self.feature_list.
        :param feature:
        :return:
        """
        try:
            return self.feature_list.index(feature)
        except ValueError:
            return None

    def has_errors(self):
        return len(self.violations) > 0

    def get_violations(self):
        return self.violations
