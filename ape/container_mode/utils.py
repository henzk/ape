from __future__ import print_function, unicode_literals
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
