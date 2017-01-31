from ape import tasks
import os
import sys


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
    '''list information about this productive environment'''
    print
    print 'root directory         :', tasks.conf.APE_ROOT
    print
    print 'active container       :', os.environ.get('CONTAINER_NAME', '')
    print
    print 'active product         :', os.environ.get('PRODUCT_NAME', '')
    print
    print 'ape feature selection  :', tasks.FEATURE_SELECTION
    print
    print 'containers and products:'
    print '-' * 30
    print
    for container_name in tasks.get_containers():
        print container_name
        for product_name in tasks.get_products(container_name):
            print '    ' + product_name
    print


@tasks.register
def cd(doi):
    '''cd to directory of interest(doi)

    a doi can be:

    herbert - the container named "herbert"
    herbert:website - product "website" located in container "herbert"
    '''
    parts = doi.split(':')
    if len(parts) == 1:
        container_name, product_name = parts[0], None
    elif len(parts) == 2:
        container_name, product_name = parts[0], parts[1]
    else:
        print 'unable to parse context - format: <container_name>:<product_name>'
        sys.exit(1)

    if container_name not in tasks.get_containers():
        print 'No such container'
    else:
        if product_name:
            if product_name not in tasks.get_products(container_name):
                print 'No such product'
            else:
                print tasks.conf.SOURCE_HEADER
                print 'cd ' + tasks.get_product_dir(container_name, product_name)
        else:
            print tasks.conf.SOURCE_HEADER
            print 'cd ' + tasks.get_container_dir(container_name)


SWITCH_TEMPLATE = '''%(source_header)s

export CONTAINER_NAME=%(container_name)s
export PRODUCT_NAME=%(product_name)s
update_ape_env
'''


@tasks.register
def switch(poi):
    '''switch context to product of interest(poi)

    a poi is:

    herbert:website - for product "website" located in container "herbert"

    After the context has been switched to herbert:website additional commands may be available
    that are relevant to herbert:website
    '''
    parts = poi.split(':')
    if len(parts) == 2:
        container_name, product_name = parts
    else:
        print 'unable to parse context: ', poi
        sys.exit(1)

    if container_name not in tasks.get_containers():
        print 'No such container'
    elif product_name not in tasks.get_products(container_name):
        print 'No such product'
    else:
        print SWITCH_TEMPLATE % dict(
            source_header=tasks.conf.SOURCE_HEADER,
            container_name=container_name,
            product_name=product_name
        )


@tasks.register
def teleport(poi):
    '''switch and cd in one operation'''
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
        print 'ERROR: this container does not exist!'
        return

    install_script = os.path.join(CONTAINER_DIR, 'install.py')
    if os.path.exists(install_script):
        print '... running install.py for %s' % container_name
        os.system('python %s' % install_script)
    else:
        print 'ERROR: this container does not provide an install.py!'
        return


@tasks.register_helper
def get_extra_pypath(container_name=None):
    from ape.installtools import pypath
    return pypath.get_extra_pypath()


@tasks.register
def export_config_to_equation(poi=None):
    """
    Generates a product.equation file for the given product name.
    It generates it from the <product_name>.config file in the products folder.
    For that you need to have your project imported to featureIDE and set the correct settings.
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
        cont_dir = os.environ.get('CONTAINER_DIR')
        equation_file_path = os.path.join(cont_dir, 'products', os.environ.get('PRODUCT_NAME'), 'product.equation')
        config_file_path = os.path.join(cont_dir, 'products', os.environ.get('PRODUCT_NAME') + '.config')
    if equation_file_path and config_file_path:
        config_new = list()
        try:
            with open(config_file_path, 'r') as config_file:
                config_old = config_file.readlines()
                for line in config_old:
                    # in FeatureIDE we cant use '.' for the paths to sub-features so we used '__'
                    # e.g. django_productline__features__development
                    if len(line.split('__')) <= 2:
                        config_new.append(line)
                    else:
                        config_new.append(line.replace('__', '.'))
        except IOError as e:
            print('Config file not found. Please make sure you have a valid .config-file in your products folder.\n'
                  ' Also make sure that this file has the same name as your product.')
        try:
            with open(equation_file_path, 'w+') as eq_file:
                eq_file.writelines(config_new)
        except IOError as e:
            print('product.equation file not found. Please make sure you have a valid product.equation in your chosen product')
    else:
        print('Please check your arguments: --poi <container>:<product>')


@tasks.register
def import_config_from_equation(poi=None):
    """
    Generates a <productname>.config file from the product.equation of the given (or activated) product name and places it in your products dir.
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
            print('Equation file not found. Please make sure you have a valid product.equation in your products/<product_name>/. \n')
        try:
            with open(config_file_path, 'w+') as config_file:
                config_file.writelines(config_new)
        except IOError as e:
            print('{product_name}.config file not found. \n '
                  'Please make sure you have a valid <product_name>.config in your products directory.'.format(product_name=product_name))
    else:
        print('Please check your arguments: --poi <container>:<product>')
