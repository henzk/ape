from __future__ import print_function, unicode_literals
import git, operator
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


class FeatureOrderValidator(object):
    """
    This class provides an API to validate the correct order of the given list of feature names
    and the passed constraints.
    """

    def __init__(self, feature_list, constraints):
        """
        Constructor
        :param feature_list: list of feature names
        :param constraints: dict(<featurename>=dict(before=[], after=[]))
        :return:
        """
        self.feature_list = feature_list
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

        feature_pos = self.feature_list.index(feature)

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
            feature_pos = self.feature_list.index(feature)

            if feature_pos != pos:
                message = '{feature} has a forced position on {pos}) but is on position {feature_pos}.'.format(
                    feature=feature,
                    pos=pos,
                    feature_pos=feature_pos
                )
                self.violations.append((feature, message))


    def has_errors(self):
        return len(self.violations) > 0

    def get_violations(self):
        return self.violations
