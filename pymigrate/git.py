__author__ = 'Maxim Styushin'
__copyright__ = 'Copyright (c)2017, Maxim Styushin'
__license__ = 'MIT'
__email__ = 'makcimkos@gmail.com'

import sys
import os
import subprocess


def get_branch(project_root: str) -> str:
    """
    Read branch name where HEAD is currently pointing to. If VERSION file exists in project_root then
    will return its contents.

    :param project_root: path to local git repo

    :return: Return current branch name if possible, 'unknown' otherwise.
    """
    if os.path.isfile(os.path.join(os.path.abspath(project_root), os.pardir, os.pardir) + '/VERSION'):
        with open(os.path.join(os.path.abspath(project_root), os.pardir, os.pardir) + '/VERSION') as f:
            return f.read().replace('\n', '')

    child = subprocess.Popen('cd {0} && git rev-parse --abbrev-ref HEAD'.format(project_root),
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
    exit_code = child.wait()
    if len(child.stdout.read()) != 0:
        branch = child.stdout.read().replace('\n', '')
    else:
        return 'unknown'
    if exit_code == 0 and branch != 'HEAD':
        return branch
    else:
        return 'unknown'


def get_latest_sha(project_dir: str, branch: str) -> str:
    """
    Read sha1 of latest commit in branch :param branch: at :param project_dir:

    :param project_dir: absolute path to project's git repo directory
    :param branch: string containing valid git branch name

    :return: sha1 commint string
    """
    child = subprocess.Popen('cd {0} && git rev-parse -q --short origin/{1}'.format(project_dir, branch),
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
    exit_code = child.wait()
    sha1 = child.stdout.read().replace('\n', '')
    if exit_code == 0:
        return sha1
    else:
        return 'unknown'


if __name__ == '__main__':
    print("This module is not callable")
    sys.exit(0)
