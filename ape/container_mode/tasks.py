from __future__ import unicode_literals, print_function
from ape import tasks
import os
import sys
import subprocess


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

    def predicate(p):
        return not p.startswith('.') and not p.startswith('_')

    products = filter(predicate, products)
    return products


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
        print('No such container')
    elif product_name not in tasks.get_products(container_name):
        print('No such product')
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
    '''installs a container'''

    CONTAINER_DIR = os.path.join(os.environ['APE_ROOT_DIR'], container_name)
    if os.path.exists(CONTAINER_DIR):
        os.environ['CONTAINER_DIR'] = CONTAINER_DIR
    else:
        print('ERROR: this container does not exist!')
        return

    install_script = os.path.join(CONTAINER_DIR, 'install.py')
    if os.path.exists(install_script):
        print('... running install.py for %s' % container_name)
        subprocess.check_call(['python', install_script])
    else:
        print(
            'ERROR: this container does not provide an install.py!')
        return


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


@tasks.register_helper
def get_feature_ide_paths(container_dir, product_name):
    """
    Takes the container_dir and the product name and returns all relevant paths from the
    feature_order_json to the config_file_path.
    :param container_dir: the full path of the container dir
    :param product_name: the name of the product
    :return: object with divert path attributes
    """
    from . import utils
    class Paths(object):
        feature_order_json = os.path.join(container_dir, '_lib/featuremodel/productline/feature_order.json')
        model_xml_path = os.path.join(container_dir, '_lib/featuremodel/productline/model.xml')
        config_file_path = os.path.join(container_dir, '_lib/featuremodel/productline/products/',
                                        utils.get_repo_name(container_dir), product_name, 'product.equation.config')
        equation_file_path = os.path.join(container_dir, 'products', product_name, 'product.equation')

    return Paths


@tasks.register
def validate_feature_model(poi=None):
    """
    Validates the order of the feature model (model.xml) against the feature ordering constraints
    :param poi: optional product of interest
    """
    from . import utils

    container_dir, product_name = tasks.get_poi_tuple(poi=poi)
    info_object = tasks.get_feature_ide_paths(container_dir, product_name)

    # lets get the feature order from the model.xml
    feature_order = utils.extract_feature_order_from_model_xml(info_object.model_xml_path)
    # lets get the ordering constraints
    ordering_constraints = utils.get_feature_order_constraints(container_dir)

    print('*** Starting feature model ordering check')
    # run the validator
    validator = utils.FeatureOrderValidator(feature_order, ordering_constraints)
    validator.check_order()
    if validator.has_errors():
        print('xxx ERROR in your model\'s feature order xxx')
        for error in validator.get_violations():
            print('\t', error[1])
        sys.exit(1)
    else:
        print('\tOK')


@tasks.register
def validate_product_equation(poi=None):
    """
    Validates the product equation.
    Currently does a feature order check.
    :param poi: optional product of interest
    """
    from . import utils

    container_dir, product_name = tasks.get_poi_tuple(poi=poi)
    feature_list = utils.get_features_from_equation(container_dir, product_name)
    ordering_constraints = utils.get_feature_order_constraints(container_dir)

    print('*** Starting product.equation ordering check')

    # run the validator
    validator = utils.ProductEquationFeatureOrderValidator(feature_list, ordering_constraints)
    validator.check_order()

    if validator.has_errors():
        print('\txxx ERROR in your product.equation feature order xxx')
        for error in validator.get_violations():
            print('\t\t', error[1])
        sys.exit(1)
    else:
        print('\tOK')


@tasks.register
def config_to_equation(poi=None):
    """
    Generates a product.equation file for the given product name.
    It generates it from the <product_name>.config file in the products folder.
    For that you need to have your project imported to featureIDE and set the correct settings.
    """

    container_dir, product_name = tasks.get_poi_tuple(poi=poi)
    info_object = tasks.get_feature_ide_paths(container_dir, product_name)
    tasks.validate_feature_model(poi=poi)

    feature_list = list()

    try:
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

            print('*** Successfully generated product.equation')
    except IOError as e:
        print('{} does not exist. Make sure your conifg file exists.'.format(info_object.config_file_path))
    try:
        with open(info_object.equation_file_path, 'w') as eq_file:
            eq_file.writelines(feature_list)
    except IOError as e:
        print(
            'product.equation file not found. Please make sure you have a valid product.equation in your chosen product')


@tasks.register
def import_config_from_equation(poi=None):
    """
    Generates a <productname>.config file from the product.equation of the given (or activated)
    product name and places it in your products dir.
    """
    import os
    config_file_path = None
    equation_file_path = None

    if poi:
        parts = poi.split(':')
        if len(parts) == 2:
            container_name, product_name = parts
            if container_name not in tasks.get_containers():
                print('No such container')
            elif product_name not in tasks.get_products(container_name):
                print('No such product')
            else:
                cont_dir = tasks.get_container_dir(container_name)
                equation_file_path = os.path.join(cont_dir, 'products', product_name, 'product.equation')
                config_file_path = os.path.join(cont_dir, 'products', product_name + '.config')
        else:
            print('Please check your arguments: --poi <container>:<product>')
    else:
        # If a product is already activated it gets selected automatically if no arguments are passed.
        product_name = os.environ.get('PRODUCT_NAME')
        cont_dir = os.environ.get('CONTAINER_DIR')
        equation_file_path = os.path.join(cont_dir, 'products', product_name, 'product.equation')
        config_file_path = os.path.join(cont_dir, 'products', product_name + '.config')
    if equation_file_path and config_file_path:
        config_new = list()
        try:
            with open(equation_file_path, 'r') as eq_file:
                config_old = eq_file.readlines()
                for line in config_old:
                    # in FeatureIDE we cant use '.' for the paths to sub-features so we used '__'
                    # e.g. django_productline__features__development
                    if not line.startswith('#'):
                        if len(line.split('.')) <= 2:
                            config_new.append(line)
                        else:
                            config_new.append(line.replace('.', '__'))
        except IOError as e:
            print(
                'Equation file not found. Please make sure you have a valid product.equation in your products/<product_name>/. \n')
        try:
            with open(config_file_path, 'w+') as config_file:
                config_file.writelines(config_new)
        except IOError as e:
            print('{product_name}.config file not found. \n '
                  'Please make sure you have a valid <product_name>.config in your products directory.'.format(
                product_name=product_name))
    else:
        print('Please check your arguments: --poi <container>:<product>')
