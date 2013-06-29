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
