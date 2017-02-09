from subprocess import check_call
import glob
import os


class VirtualEnv(object):

    def __init__(self, venv_dir):
        self.venv_dir = venv_dir
        self.bin_dir = os.path.join(venv_dir, 'bin')

    def call_bin(self, script_name, args):
        check_call([os.path.join(self.bin_dir, script_name)] + list(args))

   
    def pip_install(self, repo_url):
        self.call_bin('pip', ['install', '-e', 'git+%s' % repo_url])
        
        
    def pip_install_requirements(self, file_path):
        file_path = os.path.join(os.environ['CONTAINER_DIR'], file_path)
        self.call_bin('pip', ['install', '-r', file_path])

    
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
        
        
    
