from subprocess import check_call
import glob
import os
import sys


class VirtualEnv(object):

    def __init__(self, venv_dir):
        self.venv_dir = venv_dir
        self.bin_dir = os.path.join(venv_dir, 'Scripts' if os.name == 'nt' else 'bin')

    def call_bin(self, script_name, args):
        check_call([os.path.join(self.bin_dir, script_name)] + list(args))

    def pip_install(self, repo_url):
        self.call_bin('pip', ['install', '-e', 'git+%s' % repo_url])

    def pip_install_requirements(self, file_path):
        file_path = os.path.join(os.environ['CONTAINER_DIR'], file_path)
        self.call_bin('pip', ['install', '-r', file_path])

    def get_paths(self):
        '''
        get list of module paths
        '''

        # guess site package dir of virtualenv (system dependent)
        venv_site_packages = '%s/lib/site-packages' % self.venv_dir

        if not os.path.isdir(venv_site_packages):
            venv_site_packages_glob = glob.glob('%s/lib/*/site-packages' % self.venv_dir)

            if len(venv_site_packages_glob):
                venv_site_packages = venv_site_packages_glob[0]

        return [
            self.venv_dir,
            venv_site_packages
        ]

    def pip(self, *args):
        self.call_bin('pip', list(args))

    def python(self, *args):
        self.call_bin('python', args)

    def python_oneliner(self, snippet):
        self.python('-c', snippet)

    @staticmethod
    def create_virtualenv(venv_dir, use_venv_module=True):
        """
        creates a new virtualenv in venv_dir

        By default, the built-in venv module is used.
        On older versions of python, you may set use_venv_module to False to use virtualenv
        """

        if not use_venv_module:
            try:
                check_call(['virtualenv', venv_dir, '--no-site-packages'])
            except OSError:
                raise Exception('You probably dont have virtualenv installed: sudo apt-get install python-virtualenv')
        else:
            check_call([sys.executable or 'python', '-m', 'venv', venv_dir])
