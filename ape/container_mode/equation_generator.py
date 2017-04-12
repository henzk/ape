from __future__ import unicode_literals, print_function, division
import os
import codecs
from . import exceptions
import git


def generate_equation(container_dir, product_name):
    """
    Main public api method;
    Generates the product equation from the config file located in self.feature_model_dir.
    :return:
    """

    # first, we get the config file path and the product.equation target file path.
    config_file_path = _get_feature_model_config_file_path(container_dir, product_name)
    prod_eq_file_path = _get_product_equation_file_path(container_dir, product_name)
    # then we transform it to our custom format
    contents = _transform_config_to_equation(config_file_path)
    # finally we write the product equation-
    with codecs.open(prod_eq_file_path, 'w+') as f:
        f.writelines(contents)
    return prod_eq_file_path


def _get_feature_model_config_file_path(container_dir, product_name):
    """
    Returns the path to the feature model product equation
    """
    fp = os.path.join(
        container_dir,
        '_lib/featuremodel/productline/products',
        # get the real repository name here
        _get_real_repo_name(container_dir),
        product_name,
        'product.equation.config'
    )

    if not os.path.exists(fp):
        raise exceptions.FileDoesNotExistError(fp)
    else:
        return fp


def _get_product_equation_file_path(container_dir, product_name):
    """
    Returns the file path to the product equation.
    :return:
    """
    return os.path.join(container_dir, 'products', product_name, 'product.equation')


def _transform_config_to_equation(config_file_path):
    """
    Transforms the
    :param config_file_path:
    :return:
    """
    config_new = []

    with codecs.open(config_file_path, encoding='utf-8') as f:
        for line in f.readlines():
            # in FeatureIDE we cant use '.' for the paths to sub-features so we used '__'
            # e.g. django_productline__features__development
            config_new.append(line.replace('__', '.'))
    return ''.join(config_new)


def _get_real_repo_name(container_dir):
    """
    Returns the name of the repository of the container dir.
    This is important as the directory in our featurmodel/productline/products directory is named after the real
    repository. The actual name of the container may differ.
    E.g. in case it was checked like this: git clone myurl/myrepo.git myrepo-1
    :return: string of the name of the repository.
    """

    # Todo: first search for a name that equals the given container name, than backstep to the git repo name of
    # the container

    repo = git.Repo(container_dir)
    return repo.remotes.origin.url.split('/')[-1].split('.git')[0]
