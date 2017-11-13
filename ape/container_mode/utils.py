from __future__ import print_function, unicode_literals

import json
import os
import os.path
import xml.etree.ElementTree

import featuremonkey
import git


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

    file_path = os.path.join(container_dir, '_lib/featuremodel/productline/feature_order.json')
    with open(file_path, 'r') as f:
        ordering_constraints = json.loads(f.read())

    return ordering_constraints


def get_features_from_equation(container_dir, product_name):
    """
    :return: list of strings, each representing one feature
    """
    file_path = os.path.join(container_dir, 'products', product_name, 'product.equation')
    return featuremonkey.get_features_from_equation_file(file_path)


def _get_featuremodel_path(container_dir):
    """
    Either takes default path (relative to ape root) or, if set, the FEATUREMODEL_POOL_PATH.
    This path should be absolute and set in your initenv file, e.g. like that:

        export FEATUREMODEL_POOL_PATH=$PYTHONPATH:`/foo/bar/featuremodel`

    We assume that the featuremodel pool is placed top level in the ape root and is called "featuremodel".
    Reason: the featurepool model should be considerable for any project in your ape root and
    therefore you only need it once, not separated in every container.
    :return:
    """
    featuremodel_path = os.path.abspath(os.path.join(os.environ.get('APE_ROOT_DIR'), 'featuremodel'))
    env_path = os.environ.get('FEATUREMODEL_POOL_PATH')
    if env_path:
        featuremodel_path = env_path

    # still try a fallback to the featuremodel pool in the _lib dir in case something is wrong the the given paths
    if not os.path.exists(featuremodel_path) or not os.path.isdir(featuremodel_path):
        featuremodel_path = os.path.join(container_dir, '_lib/featuremodel')

    return featuremodel_path


def get_feature_ide_paths(container_dir, product_name):
    """
    Takes the container_dir and the product name and returns all relevant paths from the
    feature_order_json to the config_file_path.
    :param container_dir: the full path of the container dir
    :param product_name: the name of the product
    :return: object with divert path attributes
    """
    repo_name = get_repo_name(container_dir)
    featuremodel_path = _get_featuremodel_path(container_dir)

    class Paths(object):
        feature_order_json = os.path.join(featuremodel_path, 'productline/feature_order.json')
        model_xml_path = os.path.join(featuremodel_path, 'productline/model.xml')
        config_file_path = os.path.join(featuremodel_path, 'productline/products/', repo_name, product_name, 'product.equation.config')
        equation_file_path = os.path.join(container_dir, 'products', product_name, 'product.equation')
        product_spec_path = os.path.join(featuremodel_path, 'productline/products/', repo_name, 'product_spec.json')

    return Paths
