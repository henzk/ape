from __future__ import print_function, unicode_literals
import git
import operator
from . import exceptions
import xml.etree.ElementTree


def get_repo_name(repo_dir):
    """
    Takes a directory (which must be a git repo) and returns the repository name, derived from
    remote.origin.url; <domain>/foo/bar.git => bar
    :param repo_dir: path of the directory
    :return: string
    """

    repo = git.Repo(repo_dir)
    url = repo.remotes.origin.url

    return url.split('/')[-1].split('.git')[0]


def extract_feature_order_from_model_xml(file_path):
    """
    Takes the path to a FeatureIDE model.xml file and extracts the feature order.
    :param file_path: path to the model file
    :return: list of features as strings
    """

    root = xml.etree.ElementTree.parse(file_path).getroot()
    feature_order_node = root.find('featureOrder')

    features = []
    for child in feature_order_node:
        features.append(child.attrib['name'])

    return features


def get_feature_order_constraints(container_dir):
    """
    Returns the feature order constraints dict defined in featuremodel/productline/feature_order.json
    :param container_dir: the container dir.
    :return: dict
    """
    import os.path, json

    file_path = os.path.join(container_dir, '_lib/featuremodel/productline/feature_order.json')
    with open(file_path, 'r') as f:
        ordering_constraints = json.loads(f.read())

    return ordering_constraints


def get_features_from_equation(container_dir, product_name):
    """
    Takes the container dir and the product name and returns the list of features.
    :param container_dir: path of the container dir
    :param product_name: name of the product
    :return: list of strings, each representing one feature
    """
    import featuremonkey, os.path
    file_path = os.path.join(container_dir, 'products', product_name, 'product.equation')
    return featuremonkey.get_features_from_equation_file(file_path)


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
            for other in info.get(mode, []):
                other_pos = self.feature_list.index(other)
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
            raise exceptions.FeatureNotFound(
                'The specified constraint for feature "{feature}" was not found in the feature list.'.format(
                    feature=feature))

    def has_errors(self):
        return len(self.violations) > 0

    def get_violations(self):
        return self.violations


class ProductEquationFeatureOrderValidator(FeatureOrderValidator):
    """
    Validates the feature order for product equations. In contrast to the validation of the model.xml
    there may be feature defined in the constraints that do not exist in the product.equation (simply because
    this feature is not part of the product). For this reason we overwrite self.get_feature_position and
    return None for a not found feature instead of raising an exception.
    """


    def get_feature_position(self, feature):
        try:
            pos = super(ProductEquationFeatureOrderValidator, self).get_feature_position(feature)
        except exceptions.FeatureNotFound as e:
            return None
