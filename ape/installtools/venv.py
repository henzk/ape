from subprocess import call
from os.path import join as pj
import glob
import os


class VirtualEnv(object):

    def __init__(self, venv_dir):
        self.venv_dir = venv_dir
        self.bin_dir = pj(venv_dir, 'bin')

    def call_bin(self, script_name, args):
        call([pj(self.bin_dir, script_name)] + list(args))


    def pip_install(self, repo_url):
        self.call_bin('pip', ['install', '-e', 'git+%s' % repo_url])


    def pip_install_requirements(self, file_path, credentials):
        """
        Installs a given requirements.txt applying credentials.
        :param file_path: relative path to the requirements.txt
        :param credentials: a dict with username and password
        """
        file_path = pj(os.environ['CONTAINER_DIR'], file_path)
        temp_file_path = pj(os.environ['CONTAINER_DIR'], '__temp__requirements.txt')

        # read all requirements
        with open(file_path) as f:
            contents = f.read()
        # apply credentials and write temp file
        contents = contents % credentials
        with open(temp_file_path, 'w') as f:
            f.write(contents)

        # install credential-augmented requirements and finally remove temp file.
        self.call_bin('pip', ['install', '-r', temp_file_path])
        os.remove(temp_file_path)

    def get_paths(self):
        return [
            self.venv_dir,
            glob.glob('%s/lib/*/site-packages' % self.venv_dir)[0]
        ]



    # -----------------

    def pip(self, *args):
        self.call_bin('pip', list(args))

    def python(self, *args):
        self.call_bin('python', args)

    def python_oneliner(self, snippet):
        self.python('-c', snippet)
