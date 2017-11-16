from __future__ import unicode_literals, print_function

import json
import os
import subprocess
import sys

from ape import feaquencer
from ape import tasks

from . import utils
from .exceptions import ContainerError, ContainerNotFound, ProductNotFound


class Config(object):
    APE_ROOT = os.environ['APE_ROOT_DIR']
    SOURCE_HEADER = '#please execute the following in your shell:\n'


introduce_conf = Config()


@tasks.register_helper
def get_container_dir(container_name):
    return tasks.conf.APE_ROOT + '/' + container_name


@tasks.register_helper
def get_product_dir(container_name, product_name):
    return tasks.get_container_dir(container_name) + '/products/' + product_name


@tasks.register_helper
def get_containers():
    entries = os.listdir(tasks.conf.APE_ROOT)
    containers = []
    for entry in entries:
        if os.path.isdir(tasks.get_container_dir(entry) + '/products'):
            containers.append(entry)
    return containers


@tasks.register_helper
def get_products(container_name):
    products_dir = tasks.get_container_dir(container_name) + '/products'
    if not os.path.isdir(products_dir):
        return []
    products = os.listdir(products_dir)

    def is_product(p):
        return not p.startswith('.') and not p.startswith('_')

    return [p for p in products if is_product(p)]


@tasks.register
def info():
    """
    List information about this productive environment
    :return:
    """
    print()
    print('root directory         :', tasks.conf.APE_ROOT)
    print()
    print('active container       :', os.environ.get('CONTAINER_NAME', ''))
    print()
    print('active product         :', os.environ.get('PRODUCT_NAME', ''))
    print()
    print('ape feature selection  :', tasks.FEATURE_SELECTION)
    print()
    print('containers and products:')
    print('-' * 30)
    print()
    for container_name in tasks.get_containers():
        print(container_name)
        for product_name in tasks.get_products(container_name):
            print('    ' + product_name)
    print()


@tasks.register
def cd(doi):
    """
    cd to directory of interest(doi)

    a doi can be:

    herbert - the container named "herbert"
    sdox:dev - product "website" located in container "herbert"
    :param doi:
    :return:
    """

    parts = doi.split(':')

    if len(parts) == 2:
        container_name, product_name = parts[0], parts[1]
    elif len(parts) == 1 and os.environ.get('CONTAINER_NAME'):
        # interpret poi as product name if already zapped into a product in order
        # to enable simply switching products by doing ape zap prod.
        product_name = parts[0]
        container_name = os.environ.get('CONTAINER_NAME')
    else:
        print('unable to parse context - format: <container_name>:<product_name>')
        sys.exit(1)

    if container_name not in tasks.get_containers():
        print('No such container')
    else:
        if product_name:
            if product_name not in tasks.get_products(container_name):
                print('No such product')
            else:
                print(tasks.conf.SOURCE_HEADER)
                print('cd ' + tasks.get_product_dir(container_name, product_name))
        else:
            print(tasks.conf.SOURCE_HEADER)
            print('cd ' + tasks.get_container_dir(container_name))


SWITCH_TEMPLATE = '''{source_header}

export CONTAINER_NAME={container_name}
export PRODUCT_NAME={product_name}
update_ape_env
'''


@tasks.register
def switch(poi):
    """
    Zaps into a specific product specified by switch context to the product of interest(poi)
    A poi is:
        sdox:dev - for product "dev" located in container "sdox"

    If poi does not contain a ":" it is interpreted as product name implying that a product within this
    container is already active. So if this task is called with ape zap prod (and the corresponding container is
    already zapped in), than only the product is switched.

    After the context has been switched to sdox:dev additional commands may be available
    that are relevant to sdox:dev
    :param poi: product of interest, string: <container_name>:<product_name> or <product_name>.
    """

    parts = poi.split(':')
    if len(parts) == 2:
        container_name, product_name = parts
    elif len(parts) == 1 and os.environ.get('CONTAINER_NAME'):
        # interpret poi as product name if already zapped into a product in order
        # to enable simply switching products by doing ape zap prod.
        container_name = os.environ.get('CONTAINER_NAME')
        product_name = parts[0]
    else:
        print('unable to find poi: ', poi)
        sys.exit(1)

    if container_name not in tasks.get_containers():
        raise ContainerNotFound('No such container %s' % container_name)
    elif product_name not in tasks.get_products(container_name):
        raise ProductNotFound('No such product %s' % product_name)
    else:
        print(SWITCH_TEMPLATE.format(
            source_header=tasks.conf.SOURCE_HEADER,
            container_name=container_name,
            product_name=product_name
        ))


@tasks.register
def teleport(poi):
    """
    switch and cd in one operation
    :param poi:
    :return:
    """
    tasks.switch(poi)
    tasks.cd(poi)


@tasks.register
def zap(poi):
    '''alias for "teleport"'''
    tasks.teleport(poi)


@tasks.register
def install_container(container_name):
    """
    Installs the container specified by container_name
    :param container_name: string, name of the container
    """

    container_dir = os.path.join(os.environ['APE_ROOT_DIR'], container_name)
    if os.path.exists(container_dir):
        os.environ['CONTAINER_DIR'] = container_dir
    else:
        raise ContainerNotFound('ERROR: container directory not found: %s' % container_dir)

    install_script = os.path.join(container_dir, 'install.py')
    if os.path.exists(install_script):
        print('... running install.py for %s' % container_name)
        subprocess.check_call(['python', install_script])
    else:
        raise ContainerError('ERROR: this container does not provide an install.py!')


@tasks.register_helper
def get_extra_pypath(container_name=None):
    from ape.installtools import pypath
    return pypath.get_extra_pypath()


@tasks.register_helper
def get_poi_tuple(poi=None):
    """
    Takes the poi or None and returns the container_dir and the product name either of the passed poi
    (<container_name>: <product_name>) or from os.environ-
    :param poi: optional; <container_name>: <product_name>
    :return: tuple of the container directory and the product name
    """
    if poi:
        parts = poi.split(':')
        if len(parts) == 2:
            container_name, product_name = parts
            if container_name not in tasks.get_containers():
                print('No such container')
                sys.exit(1)
            elif product_name not in tasks.get_products(container_name):
                print('No such product')
                sys.exit(1)
            else:
                container_dir = tasks.get_container_dir(container_name)
        else:
            print('Please check your arguments: --poi <container>:<product>')
            sys.exit(1)
    else:
        container_dir = os.environ.get('CONTAINER_DIR')
        product_name = os.environ.get('PRODUCT_NAME')

    return container_dir, product_name


@tasks.register
def validate_product_equation(poi=None):
    """
    Validates the product equation.
    * Validates the feature order
    * Validates the product spec (mandatory functional features)
    :param poi: optional product of interest
    """
    from . import utils
    from . import validators

    container_dir, product_name = tasks.get_poi_tuple(poi=poi)
    feature_list = utils.get_features_from_equation(container_dir, product_name)
    ordering_constraints = utils.get_feature_order_constraints(container_dir)
    spec_path = utils.get_feature_ide_paths(container_dir, product_name).product_spec_path

    print('*** Starting product.equation validation')

    # --------------------------------------------------------
    # Validate the feature order
    print('\tChecking feature order')

    feature_order_validator = validators.FeatureOrderValidator(feature_list, ordering_constraints)
    feature_order_validator.check_order()

    if feature_order_validator.has_errors():
        print('\t\txxx ERROR in your product.equation feature order xxx')
        for error in feature_order_validator.get_violations():
            print('\t\t\t', error[1])
    else:
        print('\t\tOK')

    # --------------------------------------------------------
    # Validate the functional product specification
    print('\tChecking functional product spec')

    if not os.path.exists(spec_path):
        print(
            '\t\tSkipped - No product spec exists.\n'
            '\t\tYou may create a product spec if you want to ensure that\n'
            '\t\trequired functional features are represented in the product equation\n'
            '\t\t=> Create spec file featuremodel/productline/<container>/product_spec.json'
        )
        return

    spec_validator = validators.ProductSpecValidator(spec_path, product_name, feature_list)
    if not spec_validator.is_valid():
        if spec_validator.get_errors_mandatory():
            print('\t\tERROR: The following feature are missing', spec_validator.get_errors_mandatory())
        if spec_validator.get_errors_never():
            print('\t\tERROR: The following feature are not allowed', spec_validator.get_errors_never())
    else:
        print('\t\tOK')

    if feature_order_validator.has_errors() or spec_validator.has_errors():
        sys.exit(1)


@tasks.register_helper
def get_ordered_feature_list(info_object, feature_list):
    """
    Orders the passed feature list by the given, json-formatted feature
    dependency file using feaquencer's topsort algorithm.
    :param feature_list:
    :param info_object:
    :return:
    """
    feature_dependencies = json.load(open(info_object.feature_order_json))
    feature_selection = [feature for feature in [feature.strip().replace('\n', '') for feature in feature_list]
                         if len(feature) > 0 and not feature.startswith('_') and not feature.startswith('#')]
    return [feature + '\n' for feature in feaquencer.get_total_order(feature_selection, feature_dependencies)]


@tasks.register
def config_to_equation(poi=None):
    """
    Generates a product.equation file for the given product name.
    It generates it from the <product_name>.config file in the products folder.
    For that you need to have your project imported to featureIDE and set the correct settings.
    """

    container_dir, product_name = tasks.get_poi_tuple(poi=poi)
    info_object = utils.get_feature_ide_paths(container_dir, product_name)
    feature_list = list()

    try:
        print('*** Processing ', info_object.config_file_path)
        with open(info_object.config_file_path, 'r') as config_file:

            config_file = config_file.readlines()
            for line in config_file:
                # in FeatureIDE we cant use '.' for the paths to sub-features so we used '__'
                # e.g. django_productline__features__development
                if len(line.split('__')) <= 2:
                    line = line
                else:
                    line = line.replace('__', '.')

                if line.startswith('abstract_'):
                    # we skipp abstract features; this is a special case as featureIDE does not work with abstract
                    # sub trees / leafs.
                    line = ''

                feature_list.append(line)
    except IOError:
        print('{} does not exist. Make sure your config file exists.'.format(info_object.config_file_path))

    feature_list = tasks.get_ordered_feature_list(info_object, feature_list)
    feature_list.insert(0, utils.get_equation_git_string(info_object.fm_path))
    try:
        with open(info_object.equation_file_path, 'w') as eq_file:
            eq_file.writelines(feature_list)
        print('*** Successfully generated product.equation')
    except IOError:
        print('product.equation file not found. Please make sure you have a valid product.equation in your chosen product')

    # finally performing the validation of the product equation
    tasks.validate_product_equation()
